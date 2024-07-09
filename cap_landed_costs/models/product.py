from odoo import models, api, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_landed_cost_lines = fields.One2many('product.landed.cost', 'product_tmpl_id')
