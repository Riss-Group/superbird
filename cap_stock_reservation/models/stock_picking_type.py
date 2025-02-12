# -*- coding: utf-8 -*-
from pygments.lexer import default

from odoo import models, fields, api, Command


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'


    bypass_reservation = fields.Boolean(string="Bypass Reservation", default=False)


    def _get_fields_stock_barcode(self):
        return super()._get_fields_stock_barcode() + ['bypass_reservation']




