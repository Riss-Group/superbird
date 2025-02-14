# -*- coding: utf-8 -*-
from itertools import product

from odoo import models, fields, api, Command


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'


    qty_onhand_in_locations = fields.Json(compute="_compute_qty_onhand_in_locations")

    @api.depends('product_id', 'picking_location_id')
    def _compute_qty_onhand_in_locations(self):
        for line in self:
            result = []
            picking_type = line.move_id.picking_type_id

            if not (picking_type and picking_type.warehouse_id):
                line.qty_onhand_in_locations = result
                continue


            if line.location_dest_id == picking_type.warehouse_id.crossdock_location_id:
                line.qty_onhand_in_locations = result
                continue

            source_location = line.picking_location_dest_id if picking_type.is_put_away else line.picking_location_id

            # Fetch available quants in internal locations
            quants = self.env['stock.quant'].search([
                ('location_id', '!=', picking_type.warehouse_id.crossdock_location_id.id),
                ('product_id', '=', line.product_id.id),
                ('location_id', 'child_of', source_location.id),
                ('location_id.usage', '=', 'internal')
            ]).filtered(lambda q: q.available_quantity > 0)

            # Process quants directly
            result = [{
                'id': quant.location_id.id,
                'name': quant.location_id.name,
                'display_name': quant.location_id.display_name,
                'parent_path': quant.location_id.parent_path,
                'available_quantity': quant.available_quantity,
            } for quant in quants]

            # If no available stock, find the most recent move's location
            if not result:
                move = self.search([
                    ('location_dest_id', '!=', picking_type.warehouse_id.crossdock_location_id.id),
                    ('product_id', '=', line.product_id.id),
                    ('move_id.picking_type_id', '=', picking_type.id),
                    ('location_dest_id', 'child_of', source_location.id),
                    ('location_dest_id', '!=', source_location.id),
                    ('location_dest_id.usage', '=', 'internal'),
                    ('state', '=', 'done')
                ], order="date desc", limit=1)

                if move:
                    result.append({
                        'id': move.location_dest_id.id,
                        'name': move.location_dest_id.name,
                        'display_name': move.location_dest_id.display_name,
                        'parent_path': move.location_dest_id.parent_path,
                        'available_quantity': 0,
                    })

            line.qty_onhand_in_locations = result

    def _get_fields_stock_barcode(self):
        fields = super(StockMoveLine, self)._get_fields_stock_barcode()
        fields.extend(['qty_onhand_in_locations'])
        return fields