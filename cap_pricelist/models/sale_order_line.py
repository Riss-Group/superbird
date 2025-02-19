# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_pricelist_item_id(self):
        for rec in self:
            super(SaleOrderLine, rec.with_context({'partner_id': rec.order_id.partner_id,'quantity': rec.product_uom_qty}))._compute_pricelist_item_id()
