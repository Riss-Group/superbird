# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import Controller, request, route
from odoo.addons.sale_product_configurator.controllers.main import ProductConfiguratorController
from datetime import datetime
from odoo.exceptions import UserError
from odoo import fields


class ProductConfiguratorController(ProductConfiguratorController):
    
    @route('/sale_product_configurator/get_product_pricelists', type='json', auth='user')
    def get_product_pricelists(
        self,
        product_template_id,
        quantity,
        currency_id,
        company_id=None,
        only_main_product=False,
    ):

        if company_id:
            request.update_context(allowed_company_ids=[company_id])
        product_template = request.env['product.template'].browse(product_template_id)



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
            tiered_pricing = self.product_pricelist(product_template_id, combination, pricelist_id)
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
        
        # Browse the product template
        product_template = request.env['product.template'].browse(product_template_id)
        
        # Combine parent combination and the provided combination
        parent_combination = request.env['product.template.attribute.value'].browse(
            parent_combination + combination
        )

        # Loop through the accessory product's templates
        return [
            dict(
                **self._get_product_information(
                    accessory_product_template.product_tmpl_id,  # Get the product.template
                    accessory_product_template.product_tmpl_id._get_first_possible_combination(
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
    
    @route('/sale_product_configurator/get_alternate_products', type='json', auth='user')
    def sale_product_configurator_get_alternate_products(
        self,
        product_template_id,
        combination,
        parent_combination,
        currency_id,
        so_date,
        company_id=None,
        pricelist_id=None,
    ):
        # Set the context for the allowed companies if a company_id is provided
        if company_id:
            request.update_context(allowed_company_ids=[company_id])
        
        # Browse the product template
        product_template = request.env['product.template'].browse(product_template_id)
        
        # Combine parent combination and the provided combination
        parent_combination = request.env['product.template.attribute.value'].browse(
            parent_combination + combination
        )
        
        # Loop through the alternative products of the product_template and return the relevant data
        return [
            dict(
                **self._get_product_information(
                    alternate_product_template,
                    alternate_product_template._get_first_possible_combination(
                        parent_combination=parent_combination
                    ),
                    currency_id,
                    so_date,
                    parent_combination=parent_combination,
                    pricelist_id=pricelist_id,
                ),
                parent_product_tmpl_ids=[product_template.id],
            ) for alternate_product_template in product_template.alternative_product_ids
        ]




    def get_globle_data(self, pricelist_item, data, product, combination, items):
        if data.date_start:
            date_start = data.date_start.date()
        if data.date_end:
            date_end = data.date_end.date()
        current_date = date.today()
        if data.date_start and not data.date_end:
            if current_date >= date_start:
                self.get_pricelist_data(data, product, combination, items)
        elif not data.date_start and data.date_end:
            if current_date <= date_end:
                self.get_pricelist_data(data, product, combination, items)
        elif data.date_start and data.date_end:
            if current_date >= date_start and current_date <= date_end:
                self.get_pricelist_data(data, product, combination, items)
        else:
            self.get_pricelist_data(data, product, combination, items)

    def get_pricelist_data(self, pricelist_item, product, combination, items):
        if pricelist_item.compute_price == 'fixed':
            discount_per = (product.list_price - round(pricelist_item.fixed_price or 0, 2)) / product.list_price * 100
            discount_per = max(discount_per,0.0)
            if pricelist_item.currency_id and pricelist_item.currency_id.position and pricelist_item.currency_id.position == 'before':
                items.append({'quantity': pricelist_item.min_quantity, 'price': pricelist_item.currency_id.symbol + str(
                    round(pricelist_item.fixed_price or 0, 2)), 'discount_price': round(discount_per, 2)})
            elif pricelist_item.currency_id and pricelist_item.currency_id.position and pricelist_item.currency_id.position == 'after':
                items.append({'quantity': pricelist_item.min_quantity, 'price': str(round(
                    pricelist_item.fixed_price or 0, 2)) + pricelist_item.currency_id.symbol, 'discount_price': round(discount_per, 2)})
        elif pricelist_item.compute_price == 'formula' or pricelist_item.compute_price == 'percentage':
            discount_per = 0
            if pricelist_item.compute_price == 'formula':
                discount_per = pricelist_item.price_discount
            else:
                discount_per = pricelist_item.percent_price
            ProductTemplate = request.env['product.template']
            combination_p = request.env['product.template.attribute.value'].browse(
                combination)
            main_v = ProductTemplate.browse(int(product.product_tmpl_id.id))._get_combination_info(
                combination_p, int(product or 0), int(pricelist_item.min_quantity or 1))
            if pricelist_item.min_quantity > 0:
                price_dict = {'product_price': main_v.get('price')}
                if pricelist_item.currency_id and pricelist_item.currency_id.position and pricelist_item.currency_id.position == 'before':
                    # items.append({'quantity': pricelist_item.min_quantity, 'price': pricelist_item.currency_id.symbol + str(round(price_dict.get('product_price') or 0, 2))})
                    items.append({'quantity': pricelist_item.min_quantity, 'price': pricelist_item.currency_id.symbol + str(
                        round(price_dict.get('product_price') or 0, 2)), 'discount_price': discount_per})
                elif pricelist_item.currency_id and pricelist_item.currency_id.position and pricelist_item.currency_id.position == 'after':
                    # items.append({'quantity': pricelist_item.min_quantity, 'price': str(round(price_dict.get('product_price') or 0, 2)) + pricelist_item.currency_id.symbol})
                    items.append({'quantity': pricelist_item.min_quantity, 'price': str(round(price_dict.get(
                        'product_price') or 0, 2)) + pricelist_item.currency_id.symbol, 'discount_price': discount_per})

    def product_pricelist(self, product=None, combination=None, pricelist_id=None, **post):
        product_env = request.env['product.product']
        view_env = request.env['ir.ui.view']
        if int(product) != 0:
            product = product_env.sudo().browse(int(product))
            pricelist = request.env['product.pricelist'].browse(int(pricelist_id or 0))
            pricelist_item_ids = variant_id = request.env['product.pricelist.item'].search(
                [('product_id', '=', product.id),
                 ('pricelist_id', '=', pricelist.id)])
            if not variant_id:
                pricelist_item_ids = request.env['product.pricelist.item'].search(
                    [('product_tmpl_id', '=', product.product_tmpl_id.id), ('applied_on', '!=', '0_product_variant'),
                     ('pricelist_id', '=', pricelist.id)])
            currency = request.website.currency_id
            items = []
            if pricelist_item_ids:
                for pricelist_item in pricelist_item_ids:
                    self.get_globle_data(self, pricelist_item, product, combination, items)
                pricelist_items = {'pricelist_items': items}
                res = view_env._render_template('product_tiered_pricing.web_pricelist_custom', pricelist_items)
                return res
            elif pricelist and not pricelist_item_ids and pricelist.item_ids:
                flag = 0
                for data in pricelist.item_ids:
                    if data.applied_on == '2_product_category':
                        product_id = product_env.sudo().search([('id', '=', int(product.id)), ('categ_id', '=', int(data.categ_id.id))])
                        if currency.id == data.currency_id.id and product_id:
                            self.get_globle_data(self, data, product, combination, items)
                        if items:
                            flag = 1
                    elif data.applied_on == '3_global' and flag == 0:
                        if currency.id == data.currency_id.id:
                            self.get_globle_data(self, data, product, combination, items)
                pricelist_items = {'pricelist_items': items}
                return pricelist_items
            else:
                return None
        else:
            return None
