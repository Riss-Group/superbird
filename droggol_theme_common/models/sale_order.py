# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol Infotech Private Limited. (<https://www.droggol.com/>)

from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        values = super()._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, **kwargs)
        if self.website_id and not self.website_id._dr_has_b2b_access():
            for line in self.order_line:
                new_val = super()._cart_update(product_id=line.product_id.id, line_id=line.id, add_qty=-1, set_qty=0, **kwargs)
                values.update(new_val)
        return values
