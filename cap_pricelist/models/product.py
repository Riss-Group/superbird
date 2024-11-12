# -*- coding: utf-8 -*-

from odoo import models, _, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"


    main_purchase_price = fields.Float(string="Main Purchase Price", compute="_compute_main_purchase_price", store=True)

    @api.depends('seller_ids')
    def _compute_main_purchase_price(self):
        for product in self:
            product.main_purchase_price = 0
            suppliers  = product.seller_ids
            if suppliers :
                product.main_purchase_price = suppliers[0].price

    def _price_compute(self, price_type, uom=None, currency=None, company=None, date=False):
        if price_type == "purchase_main_price" :
            price = self.main_purchase_price
            return {self.id :price}
        res = super(ProductTemplate, self)._price_compute(price_type, uom, currency, company, date)
        return res



class ProductProduct(models.Model):
    _inherit = "product.product"

    main_purchase_price = fields.Float(related="product_tmpl_id.main_purchase_price")

    def _price_compute(self, price_type, uom=None, currency=None, company=None, date=False):
        if price_type == "purchase_main_price" :
            price = self.main_purchase_price
            return {self.id :price}
        res = super(ProductProduct, self)._price_compute(price_type, uom, currency, company, date)
        return res