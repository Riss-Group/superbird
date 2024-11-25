from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('alternative_product_ids')
    def _onchange_alternative_product_ids(self):
        for product in self:
            for alt_product in product.alternative_product_ids:
                if product not in alt_product.alternative_product_ids:
                    alt_product.alternative_product_ids = [(4, product.id)]

            existing_alternatives = self.env['product.template'].search([
                ('id', 'in', self.alternative_product_ids.ids)
            ])
            for alt_product in existing_alternatives:
                if alt_product not in product.alternative_product_ids:
                    alt_product.alternative_product_ids = [(3, product.id)]

    @api.model
    def create(self, vals):
        product = super().create(vals)
        if 'alternative_product_ids' in vals:
            for alt_product in product.alternative_product_ids:
                if product not in alt_product.alternative_product_ids:
                    alt_product.alternative_product_ids = [(4, product.id)]
        return product

    def write(self, vals):
        res = super().write(vals)
        if 'alternative_product_ids' in vals:
            for product in self:
                for alt_product in product.alternative_product_ids:
                    if product not in alt_product.alternative_product_ids:
                        alt_product.alternative_product_ids = [(4, product.id)]
        return res

    def get_single_product_variant(self):
        """ Method used by the product configurator to check if the product is configurable or not.

        We need to open the product configurator if the product:
        - is configurable (see has_configurable_attributes)
        - has optional products """
        res = super().get_single_product_variant()
        if res.get('product_id', False):
            has_optional_products = False
            for accessory_product in self.product_variant_id.accessory_product_ids:
                if accessory_product.product_tmpl_id.has_dynamic_attributes() or accessory_product.product_tmpl_id._get_possible_variants(
                    self.product_variant_id.product_template_attribute_value_ids
                ):
                    has_optional_products = True
                    break
            res.update({'has_optional_products': has_optional_products})
        return res