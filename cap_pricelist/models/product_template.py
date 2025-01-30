# -*- coding: utf-8 -*-

from odoo import models, _, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    main_purchase_price = fields.Monetary(string="Main Purchase Price", compute="_compute_main_purchase_price", store=True)
    sale_cost = fields.Monetary(
        'Sale Cost', company_dependent=True,
        digits='Product Price',
        compute="_compute_sale_cost",
        inverse="_set_sale_cost",
        groups="base.group_user",
        help="""Sale cost for the current company. Can be used to build pricelists independently from the standard cost"""
    )
    cost_percent_variation = fields.Float()

    @api.depends_context('company')
    @api.depends('product_variant_ids.sale_cost')
    def _compute_sale_cost(self):
        self._compute_template_field_from_variant_field('sale_cost')

    def _set_sale_cost(self):
        self._set_product_variant_field('sale_cost')

    @api.depends('seller_ids')
    def _compute_main_purchase_price(self):
        for product in self:
            product.main_purchase_price = 0
            suppliers  = product.seller_ids
            if suppliers :
                product.main_purchase_price = suppliers[0].price

    def _price_compute(self, price_type, uom=None, currency=None, company=None, date=False):
        company = company or self.env.company
        date = date or fields.Date.context_today(self)
        if price_type == "purchase_main_price" :
            return {self.id :self.main_purchase_price}
        elif price_type == 'sale_cost':
            return {self.id: self.sale_cost}
        return super(ProductTemplate, self)._price_compute(price_type, uom, currency, company, date)
