# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    crossdock_location_id = fields.Many2one('stock.location', string="Cross-Dock Location", domain="[('company_id','=', company_id)]")
