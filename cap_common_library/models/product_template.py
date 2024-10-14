from odoo import models, api, fields
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    core_cost = fields.Float('Core Cost')
    stock_class_id = fields.Many2one('product.stock_class', string='Stock Class')
    price_class_id = fields.Many2one('product.price_class', string='Price Class')
    price_subclass_id = fields.Many2one('product.price_subclass', string='Price Subclass')
    product_group_id = fields.Many2one('product.group', string='Product Group')
    product_subgroup_id = fields.Many2one('product.subgroup', string='Product Subgroup')

class ProductStockClass(models.Model):
    _name = "product.stock_class"
    _description = "Stock Class"

    name = fields.Char('Name')

class ProductPriceClass(models.Model):
    _name = "product.price_class"
    _description = "Price Class"

    name = fields.Char('Name')

class ProductPriceSubclass(models.Model):
    _name = "product.price_subclass"
    _description = "Price Subclass"

    name = fields.Char('Name')

class ProductGroup(models.Model):
    _name = "product.group"
    _description = "Product Group"

    name = fields.Char('Name')
    
class ProductSubgroup(models.Model):
    _name = "product.subgroup"
    _description = "Product Subgroup"

    name = fields.Char('Name')