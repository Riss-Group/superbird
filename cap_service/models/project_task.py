from odoo import  models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'
    _order = "priority desc, planned_date_begin desc, id desc"
    

    name = fields.Char(string='Description')
    cause = fields.Text(related='service_order_line_id.cause', store=True, readonly=False)
    correction = fields.Text(related='service_order_line_id.correction', store=True, readonly=False)
    priority = fields.Selection(selection_add=[
        ('1','low'),
        ('2','med-low'),
        ('3','med'),
        ('4','med-high'),
        ('5','high'),
    ],default='1')
    fleet_vehicle_id = fields.Many2one('fleet.vehicle')
    service_order_id = fields.Many2one('service.order')
    service_order_line_id = fields.Many2one('service.order.line')
    is_repair_service = fields.Boolean(related='project_id.is_repair_service', string="Repair Service")
    product_id = fields.Many2one('product.product', related='fleet_vehicle_id.product_id')
    product_template_variant_value_ids = fields.Many2many('product.template.attribute.value', string='Product Attributes', related='product_id.product_template_variant_value_ids')
    picking_ids = fields.One2many('stock.picking', compute="_compute_picking_ids")
    branch_company_ids = fields.Many2many('res.company', related="project_id.branch_company_ids")
    tech_notes = fields.Text()


    @api.onchange('date_deadline', 'planned_date_begin')
    def _onchange_constrain_dates(self):
        for record in self:
            if record.is_repair_service and record.service_order_id:
                if record.date_deadline and record.service_order_id.end_date and record.date_deadline > record.service_order_id.end_date:
                    raise ValidationError(_("The end date (%(date_deadline)s) cannot be later than the service order's end date (%(end_date)s)") % {
                            'date_deadline': record.date_deadline,
                            'end_date': record.service_order_id.end_date,
                        })
                if record.planned_date_begin and record.service_order_id.start_date and record.planned_date_begin < record.service_order_id.start_date:
                    raise ValidationError(_("The start date (%(planned_date_begin)s) cannot be earlier than the service order's start date (%(start_date)s)") % {
                            'planned_date_begin': record.planned_date_begin,
                            'start_date': record.service_order_id.start_date,
                        })
    
    @api.depends('service_order_line_id')
    def _compute_picking_ids(self):
        for record in self:
            group_ids = record.service_order_line_id.sale_line_ids.procurement_group_id
            record.picking_ids = self.env['stock.picking'].sudo().search([('group_id', 'in', group_ids.ids)]) if group_ids else False
    
    def action_fsm_validate(self, stop_running_timers=False):
        res = super().action_fsm_validate(stop_running_timers=stop_running_timers)
        for record in self:
            if record.project_id.is_repair_service and (not record.cause or not record.correction):
                raise UserError(_("You must enter a cause and correction before completing this task."))
            bill_type = record.service_order_line_id.bill_type
            missing_service_labor_product = record.timesheet_ids.filtered(lambda x: not x.service_labor_product_id)
            if record.project_id.is_repair_service and missing_service_labor_product and bill_type == 'actual':
                raise UserError(_("There are timesheets without a service labor product assigned to it and the billing type is based on actual labor.\
                    \n\nPlease assign an service labor prouct to all punches before closing the task."))
            done_stage_int = record._done_stage_find()
            if record.project_id.is_repair_service and done_stage_int:
                record.write({'stage_id':done_stage_int})
        return res

    def action_timer_start(self):
        res = super().action_timer_start()
        for record in self:
            if record.is_repair_service:
                wip_stage_int = record._wip_stage_find()
                if wip_stage_int:
                    record.write({'stage_id':wip_stage_int})
        return res

    def write(self, vals):
        if 'stage_id' in vals or 'state' in vals:
            for record in self.filtered(lambda x: x.project_id.is_repair_service):
                if 'stage_id' in vals and vals['stage_id'] != record.stage_id.id:
                    new_stage = self.env['project.task.type'].browse(vals['stage_id'])
                    if new_stage.is_done_stage:
                        record._validate_related_pickings()
                if 'state' in vals and vals['state'] == '1_done':
                    record._validate_related_pickings()
        return super().write(vals)

    def _done_stage_find(self):
        search_domain = [
            ('project_ids', '=', self.project_id.id),
            ('is_done_stage', '=', True)
        ]
        return self.env['project.task.type'].search(search_domain, limit=1).id
    
    def _wip_stage_find(self):
        search_domain = [
            ('project_ids', '=', self.project_id.id),
            ('is_wip_stage', '=', True)
        ]
        return self.env['project.task.type'].search(search_domain, limit=1).id

    def _validate_related_pickings(self):
        if self.picking_ids:
            incomplete_pickings = self.picking_ids.filtered(lambda p: p.state not in ['done', 'cancel'])
            if incomplete_pickings:
                raise UserError(f"You cannot mark this task as done because there are incomplete pickings: {', '.join(incomplete_pickings.mapped('name'))}")


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'


    is_done_stage = fields.Boolean()
    is_wip_stage = fields.Boolean()


class ProjectTaskCreateTimesheet(models.TransientModel):
    _inherit = 'project.task.create.timesheet'


    cause = fields.Text(related='task_id.cause', store=True, readonly=False)
    correction = fields.Text(related='task_id.correction', store=True, readonly=False)
    service_labor_product_id  = fields.Many2one('product.product', compute="_compute_service_labor_product_id", store=True, readonly=False)
    available_service_labor_product_id = fields.Many2many('product.product', compute="_compute_available_service_labor_product_id")


    @api.depends('task_id')
    def _compute_service_labor_product_id(self):
        for record in self:
            available_products = record.task_id.service_order_line_id.service_order_line_service_ids.mapped('product_id')
            if len(available_products) > 1:
                available_products = available_products[0]
            record.service_labor_product_id = available_products.id

    @api.depends('task_id.service_order_line_id.service_order_line_service_ids.product_id')
    def _compute_available_service_labor_product_id(self):
        for record in self:
            record.available_service_labor_product_id = record.task_id.service_order_line_id.service_order_line_service_ids.mapped('product_id')

    def save_timesheet(self):
        aa_line_ids = super().save_timesheet()
        if self.task_id.project_id.is_repair_service:
            aa_line_ids.write({'service_labor_product_id': self.service_labor_product_id.id})
        return aa_line_ids


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'


    service_labor_product_id  = fields.Many2one('product.product', compute="_compute_service_labor_product_id", store=True, readonly=False)
    available_service_labor_product_id = fields.Many2many('product.product', compute="_compute_available_service_labor_product_id")


    @api.depends('task_id')
    def _compute_service_labor_product_id(self):
        for record in self:
            available_products = record.task_id.service_order_line_id.service_order_line_service_ids.mapped('product_id')
            if len(available_products) > 1:
                available_products = available_products[0]
            record.service_labor_product_id = available_products.id

    @api.depends('task_id.service_order_line_id.service_order_line_service_ids.product_id')
    def _compute_available_service_labor_product_id(self):
        for record in self:
            record.available_service_labor_product_id = record.task_id.service_order_line_id.service_order_line_service_ids.mapped('product_id')