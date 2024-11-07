# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    name = fields.Char('Name', index='trigram', required=True, translate=True)
