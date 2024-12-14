# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_legacy = fields.Boolean("Is legacy")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_delivered_legacy = fields.Float("Legacy Qty Delivered")
    qty_invoiced_legacy = fields.Float("Legacy Qty Invoiced")
    is_legacy = fields.Boolean("Is legacy", related="order_id.is_legacy")


    @api.depends('qty_invoiced_legacy')
    def _compute_qty_invoiced(self):
        super(SaleOrderLine, self)._compute_qty_invoiced()
        for line in self.filtered(lambda l: l.is_legacy):
            line.qty_invoiced += line.qty_invoiced_legacy

    @api.depends('qty_delivered_legacy')
    def _compute_qty_delivered(self):
        super(SaleOrderLine, self)._compute_qty_delivered()
        for line in self.filtered(lambda l: l.is_legacy):
            line.qty_delivered += line.qty_delivered_legacy

    def _get_qty_procurement(self, previous_product_uom_qty):
        self.ensure_one()
        qty = super(SaleOrderLine, self)._get_qty_procurement(previous_product_uom_qty)
        if self.is_legacy:
            qty += self.qty_delivered_legacy
        return qty
