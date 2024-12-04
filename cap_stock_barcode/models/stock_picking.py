# -*- coding: utf-8 -*-
from odoo import models, fields, api, Command


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def button_validate(self):
        for line in self.move_line_ids:
            if line.barcode_qty_done and self.env.context.get('barcode_trigger'):
                line.qty_done = line.barcode_qty_done
        res = super(StockPicking, self).button_validate()
        return res