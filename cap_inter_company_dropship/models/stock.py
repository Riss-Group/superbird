# -*- coding: utf-8 -*-

from odoo import models, fields


class StockRoute(models.Model):
    _inherit = 'stock.route'


    dropship_default_company = fields.Many2one('res.company', string='Dropship Default Company', domain="[('id','!=', id)]")

