# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    # tracking = fields.Selection(selection_add=[
    #     ('soft_serial', 'Soft Serial Number')
    # ], ondelete={'soft_serial': 'set default'})
    soft_tracking = fields.Boolean('Soft Tracking', default=False)
    soft_serial_operation_ids = fields.Many2many('stock.picking.type')