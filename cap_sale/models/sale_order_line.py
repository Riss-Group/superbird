# -*- coding: utf-8 -*-

from odoo import fields, api, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    # Override the method to force the down payment taxes
    def _convert_to_tax_base_line_dict(self, **kwargs):
        self.ensure_one()
        res = super()._convert_to_tax_base_line_dict(**kwargs)
        if self._context.get('force_down_payment_taxes', False):
            res['taxes'] = self.company_id.sale_down_payment_product_id.taxes_id
        return res
            
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.product_id.replacement_id:
            replacement_product = self.product_id.replacement_id
            self.product_id = replacement_product
            return {
                'warning': {
                    'title': "Product Replacement",
                    'message': f"The product you selected has been replaced with {replacement_product.name}.",
                }
            }