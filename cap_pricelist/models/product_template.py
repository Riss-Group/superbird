# -*- coding: utf-8 -*-

from odoo import models, _, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    main_purchase_price = fields.Monetary(
        'Main Purchase Price',
        digits='Product Price',
        compute="_compute_main_purchase_price",
        groups="purchase.group_purchase_user",
        help="""The Main purchase price for this product. it's defined by the first applicable seller""",
        currency_id='main_purchase_currency_id',
    )
    main_purchase_currency_id = fields.Many2one(
        'res.currency',
        string='Main Purchase Price Currency',
        compute='_compute_main_purchase_price',
        groups="purchase.group_purchase_user",
    )
    sale_cost = fields.Float(
        'Sale Cost',
        digits='Product Price',
        compute="_compute_sale_cost",
        inverse="_set_sale_cost",
        store=False,
        groups="base.group_user",
        help="""Sale cost for the current company. Can be used to build pricelists independently from the standard cost"""
    )
    cost_percent_variation = fields.Float(compute='_compute_cost_percent_variation')

    @api.depends_context('company')
    @api.depends('product_variant_ids.cost_percent_variation')
    def _compute_cost_percent_variation(self):
        self._compute_template_field_from_variant_field('cost_percent_variation')

    @api.depends_context('company')
    @api.depends('product_variant_ids.sale_cost')
    def _compute_sale_cost(self):
        self._compute_template_field_from_variant_field('sale_cost')

    def _set_sale_cost(self):
        self._set_product_variant_field('sale_cost')

    @api.depends_context('company')
    @api.depends('product_variant_ids.main_purchase_price', 'product_variant_ids.main_purchase_currency_id')
    def _compute_main_purchase_price(self):
        self._compute_template_field_from_variant_field('main_purchase_price')
        self._compute_template_field_from_variant_field('main_purchase_currency_id')

    def _price_compute(self, price_type, uom=None, currency=None, company=None, date=False):
        company = company or self.env.company
        date = date or fields.Date.context_today(self)
        if price_type == "purchase_main_price" :
            return {self.id :self.main_purchase_price}
        elif price_type == 'sale_cost':
            return {self.id: self.sale_cost}
        return super(ProductTemplate, self)._price_compute(price_type, uom, currency, company, date)


    def action_sync_out_of_bound_prices(self):
        self.product_variant_ids.action_sync_out_of_bound_prices()

    def action_sync_all_prices(self):
        self.product_variant_ids.action_sync_all_prices()