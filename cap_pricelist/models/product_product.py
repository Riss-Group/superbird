# -*- coding: utf-8 -*-

from odoo import models, _, fields, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    main_purchase_price = fields.Float(related="product_tmpl_id.main_purchase_price")
    sale_cost = fields.Monetary(
        'Sale Cost', company_dependent=True,
        digits='Product Price',
        compute="_sale_cost",
        store=True,
        readonly=False,
        groups="base.group_user",
        help="""Sale cost for the current company. Can be used to build pricelists independently from the standard cost"""
    )

    @api.depends_context('company')
    @api.depends('standard_price')
    def _sale_cost(self):
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