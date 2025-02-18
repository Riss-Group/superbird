# -*- coding: utf-8 -*-

from odoo import models, fields, api


class productSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'


    @api.onchange("partner_id")
    def _get_vendor_lead_time(self):
        if self.partner_id and self.partner_id.vendor_lead_time:
            self.delay = self.partner_id.vendor_lead_time
