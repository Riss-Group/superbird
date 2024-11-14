from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    replacement_id = fields.Many2one('product.product', string="Replacement Product", help="Product that replaces this one.")
