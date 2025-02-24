# -*- coding: utf-8 -*-

from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'



    def action_confirm(self):
        action = super().action_confirm()
        if any(route.dropship_default_company for route in self.order_line.mapped('route_id')) and self.state == 'sale':
            purchase = self.sudo()._get_purchase_orders()
            purchase.sudo().button_confirm()
            self.sudo().picking_ids.filtered(lambda p: p.picking_type_id.code == "dropship").button_validate()
        return action