# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    not_done_qty = fields.Float('Qty Not Done', readonly=False, store=True)
    related_scrap_line = fields.Many2one('stock.move.line')

    @api.onchange('not_done_qty')
    def _onchange_not_done_qty(self):
        for line in self:
            if line.not_done_qty != 0:
                line.update_scrap_line()

    def update_scrap_line(self):
        for line in self:
            if line.related_scrap_line:
                line.related_scrap_line.write({'qty_done': line.not_done_qty})
            else:
                new_line = line.copy({'move_id': line.move_id.id, 'qty_done': line.not_done_qty, 'location_dest_id': line._compute_scrap_location_id()})
                line.write({'related_scrap_line' : new_line.id})

    def _compute_scrap_location_id(self):
        groups = self.env['stock.location']._read_group(
            [('company_id', 'in', self.company_id.ids), ('scrap_location', '=', True)], ['company_id'], ['id:min'])
        locations_per_company = {
            company.id: stock_warehouse_id
            for company, stock_warehouse_id in groups
        }
        return locations_per_company[self.company_id.id]
