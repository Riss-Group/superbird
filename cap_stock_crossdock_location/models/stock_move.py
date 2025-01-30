# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'


    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        if self.filtered(lambda m: m.picking_code == 'internal' and m.picking_type_id.is_put_away):
            outgoing_waiting_moves = self.search([
                ('state', 'in', ['confirmed', 'partially_available']),
                ('picking_code', '=', 'internal'),
                ('picking_type_id.is_pick', '=', True),
                ('product_id', 'in', self.mapped('product_id.id')),
                ('id', 'not in', self.ids)
            ])
            outgoing_waiting_moves.mapped('picking_id').action_assign()
        return res

    def _action_assign(self, force_qty=False):
        res = super()._action_assign(force_qty)
        skip_check_waiting_sale_picking = self.env.context.get('skip_check_waiting_sale_picking')
        for move in self:
            if move.picking_code == 'internal' and move.picking_type_id.is_pick:
                putaway_waiting_picking = self.search([
                    ('product_id', '=', move.product_id.id),
                    ('state', '=', 'assigned'),('picking_type_id.is_put_away', '=', True)
                ])
                if putaway_waiting_picking:
                    putaway_waiting_picking._check_waiting_sale_picking()

        if not skip_check_waiting_sale_picking and any(move.picking_code == 'internal' and move.picking_type_id.is_put_away for move in self):
            self.filtered(lambda m: m.picking_code == 'internal')._check_waiting_sale_picking()
            self.mapped('picking_id').with_context({'skip_check_waiting_sale_picking': True}).action_assign()

        return res

    def _check_waiting_sale_picking(self):
        """Checks and updates the move's destination for cross-docking if necessary."""
        for move in self:
            outgoing_waiting_moves = self.search([
                ('state', 'in', ['confirmed', 'partially_available']),
                ('picking_code', '=', 'internal'),
                ('picking_type_id.is_pick', '=', True),
                ('product_id', '=', move.product_id.id),
                ('id', '!=', move.id)
            ])

            crossdock_location_id = move.warehouse_id.crossdock_location_id

            if outgoing_waiting_moves and crossdock_location_id:
                sale_qty = sum(outgoing_waiting_moves.mapped('product_uom_qty'))
                move.update_move_destination_location(crossdock_location=crossdock_location_id, sale_qty=sale_qty)

    def update_move_destination_location(self, crossdock_location=False, sale_qty=0):
        """Updates the move destination location to cross-dock based on available sale quantities."""
        if not crossdock_location or not sale_qty:
            return

        # Ensure destination is not already assigned
        existing_locations = self.picking_id.move_ids.filtered(
            lambda m: m.product_id == self.product_id
        ).mapped('location_dest_id')

        if crossdock_location in existing_locations:
            return

        if self.product_uom_qty > sale_qty:
            self.copy({
                'location_dest_id': crossdock_location.id,
                'product_uom_qty': sale_qty,
            })
            self.write({'product_uom_qty': self.product_uom_qty - sale_qty})
        else:
            self.write({'location_dest_id': crossdock_location.id})
