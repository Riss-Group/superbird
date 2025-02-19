# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    is_customer_pick_up = fields.Boolean("Customer Pick-Up")

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self:
            rec.picking_ids.write({'priority': "3" if rec.is_customer_pick_up else "1" })
        return res

    @api.onchange('partner_id')
    def _compute_sale_is_customer_pick_up(self):
        for sale in self:
            if sale.partner_id and sale.partner_id.is_customer_pick_up:
                sale.is_customer_pick_up = True
            else:
                sale.is_customer_pick_up = False

