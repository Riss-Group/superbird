from odoo import  models, fields, api
from odoo.exceptions import UserError


class ServiceLineViewProduct(models.Model):
    _name = 'service.line.view.product'   
    _description = 'Service Line View Product'


    service_order_line_id = fields.Many2one('service.order.line', ondelete='cascade')
    service_order_id = fields.Many2one('service.order', related='service_order_line_id.service_order_id')
    service_order_line_product_ids = fields.One2many('service.order.line.product', related='service_order_line_id.service_order_line_product_ids',  readonly=False)
    service_order_line_service_ids = fields.One2many('service.order.line.service', related='service_order_line_id.service_order_line_service_ids',  readonly=False)
    ttype = fields.Selection([
        ('product', 'Product'),
        ('service', 'Service'),
    ])

    def action_save(self):
        return True
