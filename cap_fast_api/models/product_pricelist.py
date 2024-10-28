from odoo import models, fields, api
from datetime import datetime, timedelta


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'


    def _get_applicable_rules_api(self, product_id):
        self and self.ensure_one()
        product_id and product_id.ensure_one()
        if not self:
            return self.env['product.pricelist.item']
        pricelist_item_ids = self.env['product.pricelist.item'].with_context(active_test=False).search(self._get_applicable_rules_domain_api(product_id=product_id)).with_context(self.env.context)
        valid_pricelist_item_ids = self.env['product.pricelist.item']
        today = datetime.now()
        for pricelist_item in pricelist_item_ids:
            if not pricelist_item.date_start and not pricelist_item.date_end:
                valid_pricelist_item_ids += pricelist_item
            else:
                date_start = pricelist_item.date_start or datetime.min
                date_end = pricelist_item.date_end or datetime.max
                if date_start <= today <= date_end:
                    valid_pricelist_item_ids += pricelist_item
        return valid_pricelist_item_ids
    
    def _get_applicable_rules_domain_api(self, product_id):
        self and self.ensure_one()
        if product_id._name == 'product.template':
            templates_domain = ('product_tmpl_id', 'in', product_id.ids)
            products_domain = ('product_id.product_tmpl_id', 'in', product_id.ids)
        else:
            templates_domain = ('product_tmpl_id', 'in', product_id.product_tmpl_id.ids)
            products_domain = ('product_id', 'in', product_id.ids)
        return [
            ('pricelist_id', '=', self.id),
            '|', ('categ_id', '=', False), ('categ_id', 'parent_of', product_id.categ_id.ids),
            '|', ('product_tmpl_id', '=', False), templates_domain,
            '|', ('product_id', '=', False), products_domain,
        ]