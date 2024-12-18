from odoo import  models, fields, api
from odoo.exceptions import UserError


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
    planning_slot_ids = fields.One2many('planning.slot', 'service_task_id')
    fleet_vehicle_id = fields.Many2one('fleet.vehicle')
    service_order_id = fields.Many2one('service.order')
    service_order_line_id = fields.Many2one('service.order.line')
    is_repair_service = fields.Boolean(related='project_id.is_repair_service', string="Repair Service")
    product_id = fields.Many2one('product.product', related='fleet_vehicle_id.product_id')
    product_template_variant_value_ids = fields.Many2many('product.template.attribute.value', string='Product Attributes', related='product_id.product_template_variant_value_ids')
    picking_ids = fields.One2many('stock.picking', compute="_compute_picking_ids")
    tech_notes = fields.Text()

    @api.depends('service_order_line_id')
    def _compute_picking_ids(self):
        for record in self:
            group_ids = record.service_order_line_id.sale_line_ids.procurement_group_id
            record.picking_ids = self.env['stock.picking'].sudo().search([('group_id', 'in', group_ids.ids)]) if group_ids else False
    
    def action_fsm_validate(self, stop_running_timers=False):
        res = super().action_fsm_validate()
        for record in self:
            done_stage_int = record.done_stage_find()
            if record.project_id.is_repair_service and done_stage_int:
                record.write({'stage_id':done_stage_int})
        return res

    def done_stage_find(self):
        search_domain = [
            ('project_ids', '=', self.project_id.id),
            ('is_done_stage', '=', True)
        ]
        return self.env['project.task.type'].search(search_domain, limit=1).id

class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    is_done_stage = fields.Boolean()

class ProjectTaskCreateTimesheet(models.TransientModel):
    _inherit = 'project.task.create.timesheet'

    cause = fields.Text(related='task_id.cause', store=True, readonly=False)
    correction = fields.Text(related='task_id.correction', store=True, readonly=False)