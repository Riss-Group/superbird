# -*- coding: utf-8 -*-
from odoo import models, fields, api, Command


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