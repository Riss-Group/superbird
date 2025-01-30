# -*- coding: utf-8 -*-

from odoo import models, _, fields, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    main_purchase_price = fields.Monetary(
        'Main Purchase Price',
        digits='Product Price',
        compute="_compute_main_purchase_price",
        groups="purchase.group_purchase_user",
        help="""The Main purchase price for this product. it's defined by the first applicable seller""",
        currency_field='main_purchase_currency_id'
    )
    main_purchase_currency_id = fields.Many2one(
        'res.currency',
        string='Main Purchase Price Currency',
        compute='_compute_main_purchase_price',
    )
    sale_cost = fields.Float(
        'Sale Cost', company_dependent=True,
        digits='Product Price',
        compute="comput_sale_cost",
        store=True,
        readonly=False,
        currency_field='cost_currency_id',
        help="""Sale cost for the current company. Can be used to build pricelists independently from the standard cost"""
    )
    cost_percent_variation = fields.Float(compute='_compute_cost_percent_variation')

    @api.depends_context('company')
    @api.depends('seller_ids','seller_ids.company_id','seller_ids.price','seller_ids.sequence', 'seller_ids.currency_id')
    def _compute_main_purchase_price(self):
        for product in self:
            product.main_purchase_price = 0
            product.main_purchase_currency_id = False
            suppliers = product.seller_ids.filtered(
                lambda p: p.company_id == self.env.company or p.company_id is False)
            if suppliers:
                product.main_purchase_price = suppliers[0].price
                product.main_purchase_currency_id = suppliers[0].currency_id

    @api.depends_context('company')
    @api.depends('standard_price')
    def comput_sale_cost(self):
        for rec in self:
            rec.sale_cost = rec.standard_price

    def _price_compute(self, price_type, uom=None, currency=None, company=None, date=False):
        company = company or self.env.company
        date = date or fields.Date.context_today(self)
        self = self.with_company(company)
        if price_type == "purchase_main_price" :
            return {self.id :self.main_purchase_price}
        elif price_type == 'sale_cost':
            return {self.id: self.sale_cost}
        return super(ProductProduct, self)._price_compute(price_type, uom, currency, company, date)

    @api.depends_context('company')
    @api.depends('sale_cost', 'standard_price')
    def _compute_cost_percent_variation(self):
        for rec in self:
            rec.cost_percent_variation = ((rec.standard_price - rec.sale_cost) / rec.sale_cost) if rec.sale_cost else 0

    def action_sync_out_of_bound_prices(self):
        # Filter products where the variation is out of bounds
        out_of_bound_products = self.filtered(
            lambda p: p.cost_percent_variation > 0.05 or p.cost_percent_variation < -0.10
        )
        for product in out_of_bound_products:
            product.sale_cost = product.standard_price

    def action_sync_all_prices(self):
        # Apply to all products in the current recordset
        for product in self.filtered(lambda p: p.sale_cost != p.standard_price):
            product.sale_cost = product.standard_price