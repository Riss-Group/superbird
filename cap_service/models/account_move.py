from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'
    

    service_order_id = fields.Many2one('service.order')
    service_order_type = fields.Selection([
        ('Customer','Customer'),
        ('Warranty','Warranty'),
        ('Internal','Internal'),
    ])
    addl_service_line_ids = fields.Many2many('service.order.line', store=True, readonly=False, compute='_compute_addl_service_line_ids')
    available_service_line_ids = fields.Many2many('service.order.line', compute='_compute_available_service_line_ids')

    @api.depends('service_order_id', 'service_order_type', 'available_service_line_ids')
    def _compute_addl_service_line_ids(self):
        for record in self:
            addl_service_line_ids = self.env['service.order.line']
            if record.service_order_type == 'Customer':
                addl_service_line_ids = record.available_service_line_ids
            record.addl_service_line_ids = addl_service_line_ids
    
    @api.depends('service_order_id', 'service_order_type')
    def _compute_available_service_line_ids(self):
        for record in self:
            available_service_line_ids = self.env['service.order.line']
            if record.service_order_type == 'Customer':
                available_service_line_ids = record.service_order_id.service_order_lines.filtered(lambda x: x.ttype != 'Customer')
            record.available_service_line_ids = available_service_line_ids
    