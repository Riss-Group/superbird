# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def action_print_barcode_report(self):
        action = self.env.ref('stock.label_product_product').report_action(self)
        return action
