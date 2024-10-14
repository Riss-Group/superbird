# -*- coding: utf-8 -*-
from odoo import models, fields, api, Command


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    quarantine_location_id = fields.Many2one('stock.location', compute="_compute_scrap_location_id", store=True, readonly=False)

    def _compute_scrap_location_id(self):
        groups = self.env['stock.location']._read_group(
            [('company_id', 'in', self.company_id.ids), ('scrap_location', '=', True)], ['company_id'], ['id:min'])
        locations_per_company = {
            company.id: stock_warehouse_id
            for company, stock_warehouse_id in groups
        }
        self.quarantine_location_id =  locations_per_company[self.company_id.id]
