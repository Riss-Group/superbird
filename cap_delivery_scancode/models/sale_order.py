
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_delivery_line(self, carrier, price_unit):
        print("price_unit : ",price_unit)
        res = super(SaleOrder, self)._create_delivery_line(carrier, price_unit)
        if carrier.delivery_type == 'scancode' and carrier.scancode_user_id:
            res.name = '[ScanCode] ScanCode will remain to the customer'
        return res