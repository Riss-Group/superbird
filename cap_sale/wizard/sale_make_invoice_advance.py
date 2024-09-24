# -*- coding: utf-8 -*-

from odoo import fields, api, models

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _prepare_down_payment_lines_values(self, order):
        self.ensure_one()
        ctx = dict(self._context)
        ctx['force_down_payment_taxes'] = True
        self.env.context = ctx
        return super()._prepare_down_payment_lines_values(order)