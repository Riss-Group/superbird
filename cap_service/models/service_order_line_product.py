from odoo import  models, fields, api
from odoo.exceptions import UserError


class ServiceOrderLineProduct(models.Model):
    _name = 'service.order.line.product'  
    _description = 'Service Order Line Products' 

    service_order_line_id = fields.Many2one('service.order.line')
    product_id = fields.Many2one('product.product')
    quantity = fields.Integer()
    unit_price = fields.Float()

    def _compute_display_name(self):
        super()._compute_display_name()
        for record in self:
            record.display_name = f"{record.product_id.name}"

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            record.unit_price = record.product_id.list_price
    
    