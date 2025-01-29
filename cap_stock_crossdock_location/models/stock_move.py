# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'


    def _action_assign(self, force_qty=False):
        if self.picking_code == 'internal' and self.picking_type_id.is_pick:
            incoming_waiting_picking = self.search([('product_id','=', self.product_id.id),('state','=','confirmed')])
            incoming_waiting_picking._check_waiting_sale_picking()
        res = super(StockMove, self)._action_assign(force_qty)
        if self.picking_code == 'internal' and self.picking_type_id.is_put_away:
            self.filtered(lambda m: m.picking_code == 'internal')._check_waiting_sale_picking()
        return res

    def _check_waiting_sale_picking(self):
        for move in self:
            outgoing_waiting_moves = self.search([('state','in', ['waiting']), ('picking_code','=', 'outgoing'),
                                                  ('product_id','=', move.product_id.id),('id','!=', move.id)])
            if outgoing_waiting_moves:
                outgoing_waiting_moves.sale_line_id.move_ids
            crossdock_location_id = self.warehouse_id.crossdock_location_id
            if outgoing_waiting_moves and crossdock_location_id:
                sale_qty = sum(outgoing_waiting_moves.mapped('product_uom_qty'))
                move.update_move_destination_location(crossdock_location=crossdock_location_id, sale_qty=sale_qty)
                self.env.cr.commit

    def update_move_destination_location(self, crossdock_location=False, sale_qty=0):
        if crossdock_location and sale_qty and crossdock_location not in self.picking_id.move_ids.mapped('location_dest_id'):
            if self.quantity > sale_qty:
                #split line
                self.copy({'location_dest_id': crossdock_location.id, 'product_uom_qty':sale_qty, 'quantity':sale_qty})
                new_qty = self.product_uom_qty - sale_qty
                self.write({'product_uom_qty': new_qty, 'quantity': new_qty})
            else:
                self.write({'location_dest_id': crossdock_location.id})