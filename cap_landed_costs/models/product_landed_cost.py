from odoo import fields, api, models


class ProductLandedCost(models.Model):
    _name = 'product.landed.cost'
    _description = 'Product Landed Cost'

    product_tmpl_id = fields.Many2one('product.template')
    landed_cost_product = fields.Many2one('product.product')
    percentage = fields.Float(help="Please enter a value as decimal, 50% = 0.5")