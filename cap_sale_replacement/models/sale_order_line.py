# -*- coding: utf-8 -*-

from odoo import fields, api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    def get_replacement_history(self):
        replacement_history = []
        current_product = self.product_id

        while current_product and current_product.replacement_id:
            replacement_history.append((current_product, current_product.replacement_id))
            current_product = current_product.replacement_id

        return replacement_history

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.product_id.replacement_id:
            replacement_history = self.get_replacement_history()

            final_replacement = replacement_history[-1][1] if replacement_history else self.product_id

            self.product_id = final_replacement

            history_message = "Product Replacement History:\n\n"
            history_message += "{:<30} {:>30}\n".format("Product", "Replaced By")
            history_message += "-" * 60 + "\n"

            for product, replacement in replacement_history:
                history_message += "{:<30} {:>30}\n".format(
                    product.default_code,
                    (replacement.name or '') + ' : ' + (replacement.default_code or '')
                )

            return {
                'warning': {
                    'title': "Product Replacement",
                    'message': history_message,
                }
            }

