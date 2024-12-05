# -*- coding: utf-8 -*-

from odoo import models, api, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    soft_tracking = fields.Boolean('Soft Tracking', default=False)
    soft_serial_operation_ids = fields.Many2many('stock.picking.type')