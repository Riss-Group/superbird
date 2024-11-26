from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    eco_fee = fields.Float(string="Eco Fee", company_dependent=True, digits='Product Price')