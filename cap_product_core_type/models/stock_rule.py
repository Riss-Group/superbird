# -*- coding: utf-8 -*-


from odoo import models

class StockRule(models.Model):
    """ A rule describe what a procurement should do; produce, buy, move, ... """
    _inherit = 'stock.rule'


    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_dest_id, name, origin, company_id,
                               values):
        moves_values = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_dest_id, name, origin, company_id,
                               values)
        purchase_line_id = values.get('purchase_line_id') or False
        if purchase_line_id :
            moves_values.update({
            'purchase_line_id': purchase_line_id,
            'location_dest_id': self.env.ref('stock.stock_location_suppliers').id, # we force the dest_location here because that's the only way to use pick pack and ship to vendor
        })
        return moves_values