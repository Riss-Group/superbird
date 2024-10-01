# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    replacement_id = fields.Many2one('product.product', string='Replaced By', help='This product is replaced by the selected product.')
    replacement_ids = fields.One2many('product.product', 'replacement_id', string='Replacements', help='This product is used as a replacement for any of these listed products.')
    
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    # One2many added here to create the relation to the many2one
    replacement_ids = fields.One2many('product.product', 'replacement_id', string='Replacements', help='This product is used as a replacement for any of these listed products.')