from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    finance_term_lines = fields.One2many('sale.finance.terms', 'order_id')