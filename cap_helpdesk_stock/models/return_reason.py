# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockReturnReason(models.Model):
    _name = 'stock.return.reason'

    name = fields.Char()
