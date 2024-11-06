# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    has_core = fields.Boolean("Has Core Part")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    has_core = fields.Boolean(related="product_tmpl_id.has_core", string="Has Core Part", readonly=False)
    core_part_id = fields.Many2one('product.product', string="Core Part")
