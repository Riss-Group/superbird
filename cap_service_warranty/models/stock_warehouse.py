# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    rma_in_type_id = fields.Many2one('stock.picking.type', 'RMA In', check_company=True, copy=False)
    rma_out_type_id = fields.Many2one('stock.picking.type', 'RMA Out', check_company=True, copy=False)
