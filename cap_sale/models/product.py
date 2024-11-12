from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    replacement_id = fields.Many2one('product.product', string="Replacement Product", help="Product that replaces this one.")
    eco_fee = fields.Float(string="Eco Fee", company_dependent=True, digits='Product Price')

class ProductTemplate(models.Model):
    _inherit = 'product.template'


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