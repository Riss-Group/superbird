# -*- coding: utf-8 -*-

from odoo import models, api, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    #copy soft serial numbers from pick to pack then ship when confirming

    #maybe we dont need this
    soft_serial_ids = fields.Many2many('soft.serial.number', compute="_compute_soft_serial_ids")

    @api.depends('move_line_ids.soft_serial_ids','move_orig_ids.state')
    def _compute_soft_serial_ids(self):
        for line in self:
            serial_ids = False
            if line.move_line_ids.soft_serial_ids:
                serial_ids = line.move_line_ids.soft_serial_ids.ids
            else:
                if line.move_orig_ids:
                    serial_ids = line.move_orig_ids.soft_serial_ids.ids
            line.soft_serial_ids = serial_ids


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'


    soft_serial_ids = fields.Many2many('soft.serial.number', compute="_compute_soft_serial_ids", inverse="_inverse_soft_serial_ids",
                                       readonly=False, store=True)

    @api.depends('move_id.soft_serial_ids')
    def _compute_soft_serial_ids(self):
        for line in self:
            serial_ids = False
            if line.move_id.soft_serial_ids:
                serial_ids = line.move_id.soft_serial_ids.ids
            line.soft_serial_ids = serial_ids

    def _inverse_soft_serial_ids(self):
        for line in self:
            if line.soft_serial_ids:
                serial_ids = line.soft_serial_ids.ids
                line.move_id.soft_serial_ids = serial_ids