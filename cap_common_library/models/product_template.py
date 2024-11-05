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

    @api.onchange('price_class_id')
    def _onchange_price_class_id(self):
        if not self.price_class_id or self.price_subclass_id not in self.price_class_id.ids:
            self.price_subclass_id = False

    @api.onchange('product_group_id')
    def _onchange_product_group_id(self):
        if not self.product_group_id or self.product_subgroup_id not in self.product_group_id.ids:
            self.product_subgroup_id = False

class ProductStockClass(models.Model):
    _name = "product.stock_class"
    _description = "Stock Class"

    name = fields.Char('Name', translate=True)

class ProductPriceClass(models.Model):
    _name = "product.price_class"
    _description = "Price Class"

    name = fields.Char('Name', translate=True)
    price_subclass_ids = fields.One2many('product.price_subclass', 'price_class_id', string='Price Subclasses')


class ProductPriceSubclass(models.Model):
    _name = "product.price_subclass"
    _description = "Price Subclass"

    name = fields.Char('Name', translate=True)
    price_class_id = fields.Many2one('product.price_class', string='Price Class')


class ProductGroup(models.Model):
    _name = "product.group"
    _description = "Product Group"

    name = fields.Char('Name', translate=True)
    product_subgroup_ids = fields.One2many('product.subgroup', 'product_group_id', string='Product Subgroups')


class ProductSubgroup(models.Model):
    _name = "product.subgroup"
    _description = "Product Subgroup"

    name = fields.Char('Name', translate=True)
    product_group_id = fields.Many2one('product.group', string='Product Group')