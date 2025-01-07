# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_repayable = fields.Monetary(string="Refundable Amount", compute="_compute_total_repayable")
    refunded_amount = fields.Monetary(string="Refunded Amount", compute="_compute_total_repayable")

    def _compute_total_repayable(self):
        for sale in self:
            total_repayable = sum(sale.order_line.filtered(lambda l:l.is_core_part).mapped('price_subtotal')) or 0
            refunded_amount = sum(sale.order_line.filtered(lambda l:l.is_core_part and l.invoice_status == 'no' and l.order_id.state in ('sale') and l.core_parent_line_id.invoice_status == 'invoiced').mapped('price_subtotal')) or 0
            sale.total_repayable = total_repayable - refunded_amount
            sale.refunded_amount = refunded_amount

    def copy(self, default=None):
        sale_copy = super().copy(default)
        core_copied_lines = sale_copy.order_line.filtered(
            lambda line: line.core_parent_line_id)
        if core_copied_lines:
            core_copied_lines.unlink()
        return sale_copy