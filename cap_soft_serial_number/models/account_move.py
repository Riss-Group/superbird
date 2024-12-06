# -*- coding: utf-8 -*-

from odoo import models, api, fields

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    soft_serial_ids = fields.Many2many('soft.serial.number')

