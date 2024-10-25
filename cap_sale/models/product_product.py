# product_supercession/models/product_product.py

from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    replacement_id = fields.Many2one('product.product', string="Replacement Product", help="Product that replaces this one.")
    eco_fee_amount = fields.Float(string="Eco-Fee Amount", company_dependent=True, digits='Product Price')