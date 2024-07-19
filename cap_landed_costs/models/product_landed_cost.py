from odoo import fields, api, models
from odoo.exceptions import UserError


class ProductLandedCost(models.Model):
    _name = 'product.landed.cost'
    _description = 'Product Landed Cost'

    product_tmpl_id = fields.Many2one('product.template')
    landed_cost_product = fields.Many2one('product.product')
    percentage = fields.Float(help="Please enter a value as decimal, 50% = 0.5")

    @api.onchange('percentage')
    def _onchange_percentage(self):
        '''
            Onchange method to warn the user if they entering a suspect value
            If the value is negative we dont let them save it
        '''
        if self.percentage < 0:
            raise UserError('Percentage cannot be less than 0.')
        if not (0 <= self.percentage <= 1):
            return {
                'warning': {
                    'title': 'Warning',
                    'message': 'The percentage value should be a decimal between 0 and 1. Please confirm that this is the intended value.'
                }
            }