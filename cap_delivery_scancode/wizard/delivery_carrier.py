# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    def get_all_rates(self):
        res = super(ChooseDeliveryCarrier, self).get_all_rates()
        if self.partner_id and self.partner_id.property_delivery_carrier_id:
           rate_line_id = self.shipping_rates_all_ids.filtered(
               lambda l: l.carrier_id == self.partner_id.property_delivery_carrier_id and l.success)
           if rate_line_id:
               rate_line_id.select = True
        return res
