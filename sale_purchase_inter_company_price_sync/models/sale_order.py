# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class sale_order(models.Model):

    _inherit = "sale.order"

    @api.model
    def _prepare_purchase_order_line_data(self, so_line, date_order, company):
        res = super()._prepare_purchase_order_line_data(self, so_line, date_order, company)
        if res['price_unit'] == 0:
            res.pop('price_unit')
        res.update({
            'interco_sale_line_id': so_line.id
        })
        return res
