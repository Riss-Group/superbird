from odoo import fields, models, api


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    service_order_id = fields.Many2one('service.order')
    service_order_type = fields.Selection([
        ('customer','Customer'),
        ('warranty','Warranty'),
    ])
    
    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        vals["service_order_id"] = self.service_order_id.id
        vals["service_order_type"] = self.service_order_type
        return vals