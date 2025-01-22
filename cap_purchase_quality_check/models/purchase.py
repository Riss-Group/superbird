# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Purchase(models.Model):
    _inherit = 'purchase.order'

    quality_check_count = fields.Integer(compute='_compute_quality_check_count',)

    def _compute_quality_check_count(self):
        for order in self:
            order.quality_check_count = len(order.picking_ids.mapped('check_ids'))

    def check_quality(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quality Checks',
            'res_model': 'quality.check',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('picking_id', 'in', self.picking_ids.ids)],
        }
