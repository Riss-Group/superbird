# -*- coding: utf-8 -*-
from pygments.lexer import default

from odoo import models, fields, api


class ProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    hide_price_fields = fields.Boolean(default=False)
