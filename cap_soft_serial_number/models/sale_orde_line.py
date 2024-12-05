# -*- coding: utf-8 -*-

from odoo import models, api, fields

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    #make it compute
    soft_serial_ids = fields.Many2many('soft.serial.number', compute="_compute_soft_serial_ids")

    def _compute_soft_serial_ids(self):
        for line in self:
            line.soft_serial_ids =line.move_ids.soft_serial_ids
