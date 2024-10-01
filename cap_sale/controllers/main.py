# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import Controller, request, route
from odoo.addons.sale_product_configurator.controllers.main import ProductConfiguratorController
from datetime import datetime
from odoo.exceptions import UserError

class ProductConfiguratorController(ProductConfiguratorController):
    
    @route('/sale_product_configurator/get_part_values', type='json', auth='user')
    def get_product_part_configurator_values(
        self,
        product_template_id,
        quantity,
        currency_id,
        so_date,
        product_uom_id=None,
        company_id=None,
        pricelist_id=None,
        ptav_ids=None,
        only_main_product=False,
    ):
        if company_id:
            request.update_context(allowed_company_ids=[company_id])
        product_template = request.env['product.template'].browse(product_template_id)

        combination = request.env['product.template.attribute.value']
        if ptav_ids:
            combination = request.env['product.template.attribute.value'].browse(ptav_ids).filtered(
                lambda ptav: ptav.product_tmpl_id.id == product_template_id
            )
            # Set missing attributes (unsaved no_variant attributes, or new attribute on existing product)
            unconfigured_ptals = (
                product_template.attribute_line_ids - combination.attribute_line_id).filtered(
                lambda ptal: ptal.attribute_id.display_type != 'multi')
            combination += unconfigured_ptals.mapped(
                lambda ptal: ptal.product_template_value_ids._only_active()[:1]
            )
        if not combination:
            combination = product_template._get_first_possible_combination()
        res = dict(
            products=[
                dict(
                    **self._get_product_information(
                        product_template,
                        combination,
                        currency_id,
                        so_date,
                        quantity=quantity,
                        product_uom_id=product_uom_id,
                        pricelist_id=pricelist_id,
                    ),
                    parent_product_tmpl_ids=[],
                )
            ],
            optional_products=[
                dict(
                    **self._get_product_information(
                        optional_product_template,
                        optional_product_template._get_first_possible_combination(
                            parent_combination=combination
                        ),
                        currency_id,
                        so_date,
                        # giving all the ptav of the parent product to get all the exclusions
                        parent_combination=product_template.attribute_line_ids.\
                            product_template_value_ids,
                        pricelist_id=pricelist_id,
                    ),
                    parent_product_tmpl_ids=[product_template.id],
                ) for optional_product_template in product_template.optional_product_ids
            ] if not only_main_product else [],
            accessory_products=[
                 dict(
                    **self._get_product_information(
                        accessory_product_template.product_tmpl_id,
                        accessory_product_template.product_tmpl_id._get_first_possible_combination(
                            parent_combination=combination
                        ),
                        currency_id,
                        so_date,
                        # giving all the ptav of the parent product to get all the exclusions
                        parent_combination=product_template.attribute_line_ids.\
                            product_template_value_ids,
                        pricelist_id=pricelist_id,
                    ),
                    parent_product_tmpl_ids=[product_template.id],
                ) for accessory_product_template in product_template.accessory_product_ids
            ] if not only_main_product else [],
            alternate_products=[
                 dict(
                    **self._get_product_information(
                        alternative_product_template,
                        alternative_product_template._get_first_possible_combination(
                            parent_combination=combination
                        ),
                        currency_id,
                        so_date,
                        # giving all the ptav of the parent product to get all the exclusions
                        parent_combination=product_template.attribute_line_ids.\
                            product_template_value_ids,
                        pricelist_id=pricelist_id,
                    ),
                    parent_product_tmpl_ids=[product_template.id],
                ) for alternative_product_template in product_template.alternative_product_ids
            ] if not only_main_product else [],
            replacement_product=[
                 dict(
                    **self._get_product_information(
                        replacement_product.product_tmpl_id,
                        replacement_product.product_tmpl_id._get_first_possible_combination(
                            parent_combination=combination
                        ),
                        currency_id,
                        so_date,
                        # giving all the ptav of the parent product to get all the exclusions
                        parent_combination=product_template.attribute_line_ids.\
                            product_template_value_ids,
                        pricelist_id=pricelist_id,
                    ),
                    parent_product_tmpl_ids=[product_template.id],
                ) for replacement_product in [product_template.replacement_id]
            ] if not only_main_product else [],
        )
        return res

    @route('/sale_product_configurator/get_accessory_products', type='json', auth='user')
    def sale_product_configurator_get_accessory_products(
        self,
        product_template_id,
        combination,
        parent_combination,
        currency_id,
        so_date,
        company_id=None,
        pricelist_id=None,
    ):
        if company_id:
            request.update_context(allowed_company_ids=[company_id])
        product_template = request.env['product.template'].browse(product_template_id)
        parent_combination = request.env['product.template.attribute.value'].browse(
            parent_combination + combination
        )
        return [
            dict(
                **self._get_product_information(
                    accessory_product_template,
                    accessory_product_template._get_first_possible_combination(
                        parent_combination=parent_combination
                    ),
                    currency_id,
                    so_date,
                    parent_combination=parent_combination,
                    pricelist_id=pricelist_id,
                ),
                parent_product_tmpl_ids=[product_template.id],
            ) for accessory_product_template in product_template.accessory_product_ids
        ]