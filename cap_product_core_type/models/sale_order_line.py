# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_core_part = fields.Boolean("Is Core Part", default=False)


    def _convert_to_tax_base_line_dict(self, **kwargs):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.order_id.partner_id,
            currency=self.order_id.currency_id,
            product=self.product_id,
            taxes=self.tax_id,
            price_unit=self.price_unit,
            quantity=self.product_uom_qty if not self.is_core_part else -1 * self.product_uom_qty,
            discount=self.discount,
            price_subtotal=self.price_subtotal,
            **kwargs,
        )

    def expand_core_line(self, write=False):
        self.ensure_one()
        if self.product_id.has_core and self.product_id.core_part_id:
            for product in self.product_id.core_part_id:
                vals = self.get_sale_order_line_vals(product)
                self.create([vals])

    @api.model_create_multi
    def create(self, vals_list):
        new_vals = []
        res = self.browse()
        for elem in vals_list:
            if elem:
                product = self.env["product.product"].browse(elem.get("product_id"))
                if product and product.has_core and product.core_part_id:
                    line = super().create([elem])
                    vals_list.append(line.expand_core_line())
                else:
                    new_vals.append(elem)
        res |= super().create(new_vals)
        return res

    def get_sale_order_line_vals(self, product):
        self.ensure_one()
        quantity = self.product_uom_qty
        line_vals = {
            "order_id": self.order_id.id,
            "product_id": product.id or False,
            "company_id": self.order_id.company_id.id,
            "product_uom_qty":  - quantity,
            "is_core_part":  True,
        }

        return line_vals

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        is_core_part = self.is_core_part
        if is_core_part :
            res['is_core_part'] = self.is_core_part
            res['quantity'] *= -1
        return res
