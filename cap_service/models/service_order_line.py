from odoo import  models, fields, api, _
from odoo.exceptions import UserError
from markupsafe import Markup


class ServiceOrder(models.Model):
    _name = 'service.order.line'
    _description = "Service Order Line"
    

    op_code_id = fields.Many2one('service.template')
    name = fields.Text(string='Description')
    cause = fields.Text(compute="_compute_cause_correction", store=True, readonly=False)
    correction = fields.Text(compute="_compute_cause_correction", store=True, readonly=False)
    project_id = fields.Many2one('project.project', copy=False)
    task_id = fields.Many2one('project.task', copy=False)
    task_stage = fields.Many2one('project.task.type', related='task_id.stage_id', store=True, readonly=True)
    user_ids = fields.Many2many('res.users', related='task_id.user_ids', readonly=False)
    hours = fields.Float(string="Hours(est)", compute='_compute_hours')
    hours_consumed = fields.Float(string="Hours(consumed)", compute="_compute_hours_consumed")
    ttype = fields.Selection([
        ('Customer','Customer'),
        ('Internal','Internal'),
        ('Warranty','Warranty'),
    ],default='Customer', required=True)
    subtotal = fields.Float(compute="_compute_subtotal")
    service_order_id = fields.Many2one('service.order', ondelete='cascade')
    sale_line_ids = fields.One2many('sale.order.line', 'service_order_line_id')
    service_order_line_product_ids = fields.One2many('service.order.line.product', 'service_order_line_id',)
    service_order_line_service_ids = fields.One2many('service.order.line.service', 'service_order_line_id',)
    sequence = fields.Integer()
    task_attachment_ids = fields.One2many('ir.attachment', related='task_id.attachment_ids')
    task_attachment_count = fields.Integer(string="Attachment Count", compute="_compute_task_attachment_count", store=False)
    service_template_id = fields.Many2one('service.template')
    
    
    @api.depends('task_id.timesheet_ids.unit_amount')
    def _compute_hours_consumed(self):
        for record in self:
            record.hours_consumed = sum(record.task_id.timesheet_ids.mapped('unit_amount'))
    
    @api.depends('service_order_line_service_ids.quantity')
    def _compute_hours(self):
        for record in self:
            record.hours = sum(record.service_order_line_service_ids.mapped('quantity'))
    
    @api.depends('service_order_line_service_ids.quantity', 'service_order_line_service_ids.unit_price', 'service_order_line_product_ids.quantity', 'service_order_line_product_ids.unit_price' )
    def _compute_subtotal(self):
        for record in self:
            subtotal = 0
            subtotal += sum([x.quantity * x.unit_price for x in record.service_order_line_product_ids])
            subtotal += sum([x.quantity * x.unit_price for x in record.service_order_line_service_ids])
            record.subtotal = subtotal
    
    @api.depends('task_id.cause', 'task_id.correction')
    def _compute_cause_correction(self):
        for record in self:
            record.cause = record.task_id.cause
            record.correction = record.task_id.correction
    
    @api.depends('task_id')
    def _compute_task_attachment_count(self):
        for record in self:
            record.task_attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'project.task'),
                ('res_id', '=', record.task_id.id)
            ])
    
    def button_view_attachments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attachments',
            'view_mode': 'kanban',
            'res_model': 'ir.attachment',
            'views': [
                (self.env.ref('cap_service.view_attachment_kanban_preview').id, 'kanban'),
            ],
            'domain': [('res_model', '=', 'project.task'), ('res_id', '=', self.task_id.id)],
            'target': 'current',
        }

    def button_view_products(self):
        '''
            Service Line ID is passed through context

            Returns:
                Window Action
        '''
        return {
            'name': 'View/Add Products',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'service.line.view.product',
            'context': {
                'default_service_order_line_id': self.id,
                'default_ttype': 'product'
            },
            'target': 'new',
        }
    
    def button_view_services(self):
        '''
            Service Line ID is passed through context

            Returns:
                Window Action
        '''
        return {
            'name': 'View/Add Services',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'service.line.view.product',
            'context': {
                'default_service_order_line_id': self.id,
                'default_ttype': 'service'
            },
            'target': 'new',
        }
    
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for service_order in records.mapped('service_order_id'):
            service_order_lines = service_order.service_order_lines.filtered(lambda line: line.id in records.ids)
            msg = Markup("<b>%s</b><ul>") % _("Service Lines Created:")
            for line in service_order_lines:
                msg += Markup("<li><b>Type:</b> %s, <b>Name:</b> %s</li>") % (
                    line.ttype or 'N/A',
                    line.name or 'N/A'
                )
            msg += Markup("</ul>")
            service_order.message_post(body=msg,subtype_xmlid="mail.mt_note")
        return records

    def unlink(self):
        service_orders = self.mapped('service_order_id')
        for service_order in service_orders:
            service_order_lines = self.filtered(lambda line: line.service_order_id == service_order)
            msg = Markup("<b>%s</b><ul>") % _("Service Lines Deleted:")
            for line in service_order_lines:
                msg += Markup("<li><b>Sequence:</b> %s, <b>Description:</b> %s</li>") % (
                    line.sequence or 'N/A',
                    line.name or 'N/A'
                )
            msg += Markup("</ul>")
            service_order.message_post(body=msg,subtype_xmlid="mail.mt_note")
        return super().unlink()