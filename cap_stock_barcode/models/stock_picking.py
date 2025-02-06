# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def button_validate(self):
        for line in self.move_line_ids:
            if line.barcode_qty_done and self.env.context.get('barcode_trigger') and not line.is_splited:
                line.qty_done = line.barcode_qty_done
        res = super(StockPicking, self).button_validate()
        return res

    def _get_stock_barcode_data(self):
        data = super(StockPicking, self)._get_stock_barcode_data()
        for picking in data.get('records').get('stock.picking', []):
            pick = self.browse(picking.get('id'))
            picking['name'] = pick.origin + ' ( ' + pick.name + ' ) ' if pick.origin  else pick.name
        return data

    def _package_move_lines(self, batch_pack=False):
        # because in the barcode we are using new field barode_qty_done we need to filter by it instead of quantity if we are using the barcode app
        barcode_view = self.env.context.get('barcode_view')
        if barcode_view:
            if len(self.picking_type_id) > 1:
                raise UserError(_("You cannot pack products into the same package when they are from different transfers with different operation types."))
            quantity_move_line_ids = self.move_line_ids.filtered(
                lambda ml:
                    float_compare(ml.barcode_qty_done, 0.0, precision_rounding=ml.product_uom_id.rounding) > 0 and
                    not ml.result_package_id
            )
            move_line_ids = quantity_move_line_ids.filtered(lambda ml: ml.picked)
            if not move_line_ids:
                move_line_ids = quantity_move_line_ids
            if self.env.context.get('move_lines_to_pack_ids', False):
                move_line_ids = move_line_ids.filtered(lambda ml: ml.id in self.env.context['move_lines_to_pack_ids'])
            return move_line_ids
        else:
            return super(StockPicking, self)._package_move_lines(batch_pack)