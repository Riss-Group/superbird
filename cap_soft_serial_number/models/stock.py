# -*- coding: utf-8 -*-
from itertools import product

from odoo import models, api, fields
from odoo.tools.populate import compute


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


    barcode_qty_done = fields.Float('Qty Done', compute="_compute_barcode_qty_done", readonly=False, store=True)
    show_serial = fields.Boolean(compute="_show_serial")
    soft_serial_ids = fields.Many2many('soft.serial.number', compute="_compute_soft_serial_ids", inverse="_inverse_soft_serial_ids",
                                       readonly=False, store=True)

    @api.depends('product_id','move_id')
    def _show_serial(self):
        for line in self:
            show_serial = False
            product = line.product_id
            if product and line.move_id and line.move_id.picking_type_id.id in product.soft_serial_operation_ids.ids:
                show_serial =True
            line.show_serial = show_serial

    @api.depends('soft_serial_ids')
    def _compute_barcode_qty_done(self):
        for line in self:
            line.barcode_qty_done = 0
            if line.soft_serial_ids:
                line.barcode_qty_done = len(line.soft_serial_ids)

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