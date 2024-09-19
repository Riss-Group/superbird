# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_core_part = fields.Boolean("Is Core Part", default=False)

    @api.depends('move_ids.state', 'move_ids.scrapped', 'move_ids.quantity', 'move_ids.product_uom')
    def _compute_qty_delivered(self):
        super(SaleOrderLine, self)._compute_qty_delivered()
        if self.is_core_part:
            self.qty_delivered *= -1

    def _get_qty_procurement(self, previous_product_uom_qty=False):
        if self.is_core_part:
            qty = self.product_uom_qty * 2
            return qty
        else:
            return super(SaleOrderLine, self)._get_qty_procurement(previous_product_uom_qty)

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
            "product_uom_qty":  quantity,
            "is_core_part":  True,
        }

        return line_vals

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        is_core_part = self.is_core_part
        if is_core_part :
            res['is_core_part'] = self.is_core_part
        return res
