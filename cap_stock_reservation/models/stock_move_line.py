# -*- coding: utf-8 -*-
from itertools import product

from odoo import models, fields, api, Command


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'


    qty_onhand_in_locations = fields.Char(string="On Hand Locations", compute="_compute_qty_onhand_in_locations")


    @api.depends( 'product_id', 'picking_location_id')
    def _compute_qty_onhand_in_locations(self):
        for line in self:
            result = []
            quants = self.env['stock.quant'].search([
                ('product_id','=', line.product_id.id),('location_id','child_of', line.picking_location_id.id)]).filtered(
                lambda l: l.available_quantity > 0)
            for quant in quants :
                result.append({
                    'id' : quant.location_id.id,
                    'name' : quant.location_id.name,
                    'display_name' : quant.location_id.display_name,
                    'parent_path' : quant.location_id.parent_path,
                    'available_quantity' : quant.available_quantity,
                })
            line.qty_onhand_in_locations = result

    def _get_fields_stock_barcode(self):
        fields = super(StockMoveLine, self)._get_fields_stock_barcode()
        fields.extend(['qty_onhand_in_locations'])
        return fields