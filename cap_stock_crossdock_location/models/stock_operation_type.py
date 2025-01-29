# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'


    is_put_away = fields.Boolean('Is Put Away')
    is_pick = fields.Boolean('Is Pick')
    is_pack = fields.Boolean('Is Pack')

