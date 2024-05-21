from odoo import models, fields, api
from odoo.exceptions import UserError


class ServiceOrderLineProduct(models.Model):
    _name = 'service.order.line.product'
    _description = 'Service Order Line Products'

    service_order_line_id = fields.Many2one('service.order.line', required=False)
    service_order_id = fields.Many2one('service.order',
                                       related='service_order_line_id.service_order_id',
                                       readonly=True,
                                       store=True)
    so_line_ids = fields.One2many('sale.order.line', 'service_order_line_product_id')
    task_ids = fields.Many2many('project.task', compute='_get_task_ids')
    product_id = fields.Many2one('product.product', required=True)
    product_type = fields.Selection(related='product_id.type', store=True)
    quantity = fields.Integer()
    unit_price = fields.Float()
    warranty_coverage = fields.Selection([('customer', 'Customer'),
                                          ('warranty', 'Warranty'),
                                          ('internal', 'internal')],
                                         required=True)

    @api.depends('so_line_ids.task_id')
    def _get_task_ids(self):
        for rec in self:
            rec.task_ids = rec.so_line_ids.mapped('task_id')

    def _compute_display_name(self):
        super()._compute_display_name()
        for record in self:
            record.display_name = f"{record.product_id.name}"

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            record.unit_price = record.product_id.list_price

    