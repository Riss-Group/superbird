# -*- coding: utf-8 -*-

from odoo import models, _


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    #If there are multiple applicable rules. Choose the cheapest
    def _get_applicable_rules(self, products, date, **kwargs):
        res = super(Pricelist, self)._get_applicable_rules(products, date, **kwargs)
        applicable_rules = []
        for product in products:
            product_uom = product.uom_id

            qty_in_product_uom = self.env.context.get('quantity') or 1

            applicable_rules = [rule for rule in res if rule._is_applicable_for(product, qty_in_product_uom)]
            currency = self.currency_id or self.env.company.currency_id

        if applicable_rules:
            applicable_rules.sort(key=lambda rule: rule._compute_price(
                product, qty_in_product_uom, product_uom, date=date, currency=currency))
            return applicable_rules

        return res