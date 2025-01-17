# -*- coding: utf-8 -*-
from pygments.lexer import default

from odoo import models, fields, api, Command


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    quarantine_location_id = fields.Many2one('stock.location', compute="_compute_scrap_location_id", store=True, readonly=False)
    split_lines = fields.Boolean(string="Split Lines", default=False)
    machinegun_scan = fields.Boolean(string="machinegun Scan", default=False)

    def _get_fields_stock_barcode(self):
        return super()._get_fields_stock_barcode() + ['split_lines', 'machinegun_scan', 'barcode_validation_full']


    def _compute_scrap_location_id(self):
        for record in self:
            groups = self.env['stock.location']._read_group(
                [('company_id', '=', record.company_id.id), ('scrap_location', '=', True)],
                ['company_id'],
                ['id:min']
            )

            locations_per_company = {
                company_id: stock_warehouse_id
                for company_id, stock_warehouse_id in groups
            }

            record.quarantine_location_id = locations_per_company.get(record.company_id.id, False)

