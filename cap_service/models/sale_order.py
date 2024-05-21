from odoo import fields, models, api


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    service_order_id = fields.Many2one('service.order')
    