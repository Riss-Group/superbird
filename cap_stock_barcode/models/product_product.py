# -*- coding: utf-8 -*-
from pygments.lexer import default

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_oversize = fields.Boolean('Oversize', default=False)

    def action_print_barcode_report(self):
        action = self.env.ref('stock.label_product_product').report_action(self)
        return action
