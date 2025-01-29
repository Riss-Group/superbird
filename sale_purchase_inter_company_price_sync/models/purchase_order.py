# -*- coding: utf-8 -*-
from odoo import api, fields, models, Command, _
from odoo.exceptions import UserError


class purchase_order(models.Model):

    _inherit = "purchase.order"
    @api.model
    def _prepare_sale_order_line_data(self, line, company):
        res = super()._prepare_sale_order_line_data(line, company)
        if res['price_unit'] == 0:
            res.pop('price_unit')
        res.update({
            'interco_purchase_line_id': line.id
        })
        return res
