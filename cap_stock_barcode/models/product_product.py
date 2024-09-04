# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def action_print_barcode_report(self):
        action = self.env.ref('product.action_report_pricelist').report_action(self)
        return action
