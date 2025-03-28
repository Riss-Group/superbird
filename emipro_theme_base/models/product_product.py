# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_brand_id = fields.Many2one('product.brand', related='product_tmpl_id.product_brand_id')

    def _website_show_quick_add(self):
        website = self.env['website'].get_current_website()
        res = False
        check_hide_add_to_cart = True if website.b2b_hide_add_to_cart and website.is_public_user() else False
        if not check_hide_add_to_cart:
            res = super(ProductProduct, self)._website_show_quick_add()
        return res

    def remove_cart_button(self):
        if self.detailed_type == 'product' and not self.allow_out_of_stock_order and self.sudo().with_context(
                warehouse=request.website._get_warehouse_available()).free_qty < 1:
            return True
        return False