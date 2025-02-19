# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_legacy = fields.Boolean("Is legacy", readonly=True, store=True, default=False)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    qty_received_legacy = fields.Float("Legacy Qty Received")
    qty_invoiced_legacy = fields.Float("Legacy Qty Invoiced")
    is_legacy = fields.Boolean("Is legacy", related="order_id.is_legacy")

    @api.depends('qty_invoiced_legacy')
    def _compute_qty_invoiced(self):
        super(PurchaseOrderLine, self)._compute_qty_invoiced()
        for line in self.filtered(lambda l: l.is_legacy):
            line.qty_invoiced += line.qty_invoiced_legacy


    @api.depends('qty_received_legacy')
    def _compute_qty_received(self):
        super(PurchaseOrderLine, self)._compute_qty_received()
        for line in self.filtered(lambda l: l.is_legacy):
            line.qty_received += line.qty_received_legacy


    def _get_qty_procurement(self):
        self.ensure_one()
        qty = super(PurchaseOrderLine, self)._get_qty_procurement()
        if self.is_legacy:
            qty += self.qty_received_legacy
        return qty