# -*- coding: utf-8 -*-

from odoo import models, fields, api
import ast


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_domain = fields.Char(compute="_compute_product_domain", store=True)


    @api.depends('order_id.partner_id')
    def _compute_product_domain(self):
        for line in self:
            partner = line.order_id.partner_id
            combined_domain = []
            if partner:
                combined_domain = line._get_partner_restrictions(partner=partner)
        line.product_domain = combined_domain + [('sale_ok', '=', True)]


    def _get_partner_restrictions(self, partner=False):
        if not partner:
            return []
        restrictions = self.env['sale.restriction'].search(
            [('customer_domain', '!=', False), ('allowed_products', '!=', False)])
        if not restrictions:
            return []

        partner_obj = self.env['res.partner']
        combined_domain = []
        for restriction in restrictions:
            customer_domain = ast.literal_eval(restriction.customer_domain)
            if partner_obj.search_count(customer_domain+ [('id', '=', partner.id)]):
                product_domain = ast.literal_eval(restriction.allowed_products)
                if combined_domain:
                    combined_domain = combined_domain + product_domain
                    # combined_domain = ['|'] + combined_domain + product_domain
                else:
                    combined_domain = product_domain
        return combined_domain
