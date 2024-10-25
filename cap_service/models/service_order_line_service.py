from odoo import  models, fields, api
from odoo.exceptions import UserError


class ServiceOrderLineService(models.Model):
    _name = 'service.order.line.service'  
    _description = 'Service Order Line Service' 

    service_order_line_id = fields.Many2one('service.order.line', ondelete='cascade')    
    sale_line_id = fields.One2many('sale.order.line', 'service_order_line_service_id')
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
    
    def write(self, vals):
        if 'service_order_line_id' in vals and not vals['service_order_line_id']:
            self.unlink()
            return True
        return super().write(vals)