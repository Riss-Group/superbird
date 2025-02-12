# -*- coding: utf-8 -*-
from itertools import product

from odoo import models, fields, api, Command


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    not_done_qty = fields.Float('Qty Not Done', readonly=False, store=True)
    qty_remaining = fields.Float('Remaining Qty', compute="compute_remaining_qty", store=False)
    related_scrap_line = fields.Many2one('stock.move.line')
    barcode_qty_done = fields.Float('Qty Done', store=True)
    product_uom_qty = fields.Float(related="move_id.product_uom_qty")
    is_quarantine = fields.Boolean(default=False)
    is_splited = fields.Boolean(default=False)
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

    # @api.onchange('not_done_qty')
    def _onchange_not_done_qty(self):
        for line in self:
            if line.not_done_qty != 0:
                line.update_scrap_line()
            else:
                if line.related_scrap_line:
                    line.related_scrap_line.unlink()
                else :
                    update_dict = {'is_quarantine':False}
                    if line.move_id.picking_id and line.move_id.picking_id.location_dest_id:
                        update_dict.update({'location_dest_id': line.move_id.picking_id.location_dest_id.id})
                    line.update(update_dict)

    @api.depends( 'move_id.product_uom_qty', 'barcode_qty_done', 'not_done_qty')
    def compute_remaining_qty(self):
        for line in self:
            line.qty_remaining = line.move_id.product_uom_qty - line.barcode_qty_done - line.not_done_qty

    def update_scrap_line(self):
        for line in self:
            if line.related_scrap_line:
                line.related_scrap_line.update({'barcode_qty_done': line.not_done_qty})
            else:
                scrap_location = line.picking_type_id.quarantine_location_id.id or line.get_scrap_location()
                if line.product_uom_qty == 1 :
                    line.update({'location_dest_id': scrap_location, 'is_quarantine':True, 'barcode_qty_done':1, 'not_done_qty':0})
                else:
                    new_move = line.move_id.copy({
                        'product_uom_qty': line.not_done_qty, 'location_dest_id': scrap_location
                    })
                    new_line = line.copy({
                        'move_id': new_move.id,
                        'qty_done': line.not_done_qty,
                        'barcode_qty_done': line.not_done_qty,
                        'location_dest_id': scrap_location,
                        'is_quarantine': True
                    })

                    line.update({'related_scrap_line' : new_line.id})
                    # self.env.cr.execute(f"update stock_move set product_uom_qty={line.move_id.product_uom_qty - line.not_done_qty} where id={line.move_id.id}")
                    new_move.picking_id.action_confirm()

    def _compute_scrap_location_id(self):
        groups = self.env['stock.location']._read_group(
            [('company_id', 'in', self.company_id.ids), ('scrap_location', '=', True)], ['company_id'], ['id:min'])
        locations_per_company = {
            company.id: stock_warehouse_id
            for company, stock_warehouse_id in groups
        }
        return locations_per_company[self.company_id.id]

    def update_product_barcode(self, barcode):
        if barcode:
            self.product_id.write({'barcode_ids': [
                Command.create({
                    'product_id': self.product_id.id,
                    'name': barcode,
                })]
            })
        return True

    def _get_fields_stock_barcode(self):
        fields = super(StockMoveLine, self)._get_fields_stock_barcode()
        fields.extend(['barcode_qty_done', 'product_uom_qty', 'origin', 'is_quarantine','not_done_qty','is_splited', 'qty_onhand_in_locations'])
        return fields

    def get_scrap_location(self):
        groups = self.env['stock.location']._read_group(
            [('company_id', 'in', self.company_id.ids), ('scrap_location', '=', True)], ['company_id'], ['id:min'])
        locations_per_company = {
            company.id: stock_warehouse_id
            for company, stock_warehouse_id in groups
        }
        for scrap in self:
            return locations_per_company[scrap.company_id.id]

    def write(self, vals):
        super(StockMoveLine, self).write(vals)
        save_qty_not_done = self.env.context.get('onchange_not_done_qty')
        if not save_qty_not_done and 'not_done_qty' in vals.keys():
            for line in self:
                line.with_context({'onchange_not_done_qty' : True})._onchange_not_done_qty()



class StockMoveLineMail(models.Model):
    _name = 'stock.move.line'
    _inherit = 'stock.move.line'
    _inherit = ['stock.move.line', 'mail.thread', 'mail.activity.mixin']
