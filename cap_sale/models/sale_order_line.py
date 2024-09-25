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
            
