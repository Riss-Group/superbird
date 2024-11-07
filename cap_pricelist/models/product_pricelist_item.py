# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import ast


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"


    base = fields.Selection(selection_add=[('purchase_main_price', 'Purchase Main Price')],
                                  ondelete={'purchase_main_price': 'set default'})
    applied_on = fields.Selection(selection_add=[('4_product_domain', 'Domain')],
                                  ondelete={'4_product_domain': 'set default'})
    product_domain = fields.Char("Domain")



    @api.depends('applied_on', 'categ_id', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price', \
        'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge')
    def _compute_name_and_price(self):
        super(PricelistItem, self)._compute_name_and_price()
        for item in self:
            if item.product_domain and item.applied_on == '4_product_domain':
                item.name = _("Domain: %s", item.product_domain)



    def _is_applicable_for(self, product, qty_in_product_uom):
        res = super(PricelistItem, self)._is_applicable_for(product, qty_in_product_uom)
        if self.applied_on == "4_product_domain" and self.product_domain :
            product_domain = ast.literal_eval(self.product_domain)
            if product._name == 'product.template':
                applicable_products = self.env['product.template'].search(product_domain)
            else:
                applicable_products = self.env['product.product'].search(product_domain)
            if product not in applicable_products:
                res = False
        return res
