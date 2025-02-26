import logging
from datetime import datetime
from odoo import http
from odoo.http import request, route
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import WebsiteSale
from werkzeug.datastructures import ImmutableOrderedMultiDict
from odoo.addons.emipro_theme_base.controllers.main import WebsiteSaleExt
from odoo.addons.website.controllers.main import QueryURL
from odoo.osv import expression
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools import lazy, str2bool
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.addons.website.models.ir_http import sitemap_qs2dom
_logger = logging.getLogger(__name__)

class CustomWebsiteSaleExt(WebsiteSaleExt):
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        try:
            min_price = float(min_price)
        except ValueError:
            min_price = 0
        try:
            max_price = float(max_price)
        except ValueError:
            max_price = 0

        website = request.env['website'].get_current_website()
        ppr = http.request.env['website'].get_current_website().shop_ppr or 4
        ppg = http.request.env['website'].get_current_website().shop_ppg or 20
        request_args = request.httprequest.args

        discount = False

        if 'discount' in post.get('order', ''):
            order = post.pop('order')
            discount = True

        Category = request.env['product.public.category']
        if category:
            category_item = Category.search([('id', '=', int(category))], limit=1)
            if not category_item or not category_item.can_access_from_current_website():
                raise NotFound()
            category_children = Category.search([('parent_id', '=', category_item.id)], order="sequence asc")
            category_products = []
            if category_item.child_id:
                values = {
                    'category': category_item,
                    'category_products': category_children
                }
                return request.render("cap_eshop.children_categories_list", values)
        else:
            category = Category
            Categories = request.env['product.public.category']
            categories = Categories.search([], order="sequence asc")
            category_products = []
            for category in categories:
                if not category.parent_id and category.child_id:
                    child_categories = category.child_id.sorted(lambda c: c.sequence)
                    category_products.append({
                        'category': category,
                        'children': child_categories,
                    })
            
            values = {
                'category': None,
                'category_products': category_products
            }
            return request.render("cap_eshop.all_categories_list", values)

        res = super(WebsiteSaleExt, self).shop(page=page, category=category, search=search, min_price=min_price,
                                               max_price=max_price, ppg=ppg, **post)

        products = res.qcontext.get('products')
        def sort_function(value):
            list_price = value.get('list_price', 0)
            price = value.get('price', 0)
            if list_price > price:
                return (list_price - price) / list_price
            else:
                return 0

        if discount:
            product_prices_data = list(map(lambda product: product._get_combination_info(), products))
            product_prices_data.sort(key=sort_function, reverse=True)
            res.qcontext.update(products=request.env['product.template'].browse(list(map(lambda p: p.get('product_template_id'), product_prices_data))))

        bins = TableCompute().process(res.qcontext.get('products'), ppg, ppr)

        if post.get('brand', False):
            url = f"""/shop/brands/{slug(post.get('brand', False))}"""
            product_count = len(request.env['product.template'].search(
                [('sale_ok', '=', True), ('website_id', 'in', (False, request.website.id)),
                 ('product_brand_id', '=', post.get('brand', False).id), ]))

            pager = website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=None)

            Category = request.env['product.public.category'].sudo()
            search_categories = Category.search(
                [('product_tmpl_ids', 'in', res.qcontext.get('search_product').ids)]).parents_and_self

            res.qcontext.update(
                {'pager': pager, 'products': res.qcontext.get('products'), 'bins': bins, 'search_count': product_count,
                 'brand_val': post.get('brand', False), 'categories': search_categories})

        # Create Report for the search keyword
        curr_website = request.website.get_current_website()
        if search and curr_website.enable_smart_search:
            search_term = ' '.join(search.split()).strip().lower()
            attrib = res.qcontext.get('attrib_values', False)
            if search_term and not category and not attrib and page == 0:
                request.env['search.keyword.report'].sudo().create({
                    'search_term': search_term,
                    'no_of_products_in_result': res.qcontext.get('search_count', 0),
                    'user_id': request.env.user.id
                })

        product_ids = res.qcontext.get('search_product', request.env['product.template'].sudo())

        # preapare count and search details parametres
        attrib_list = request_args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        filter_by_price_enabled = website.is_view_active('website_sale.filter_products_price')
        if filter_by_price_enabled:
            company_currency = website.company_id.currency_id
            conversion_rate = request.env['res.currency']._get_conversion_rate(
                company_currency, website.currency_id, request.website.company_id, fields.Date.today())
        else:
            conversion_rate = 1

        filter_by_tags_enabled = website.is_view_active('website_sale.filter_products_tags')
        if filter_by_tags_enabled:
            tags = request_args.getlist('tags')
            # Allow only numeric tag values to avoid internal error.
            if tags and all(tag.isnumeric() for tag in tags):
                post['tags'] = tags
            else:
                post['tags'] = None

        # Category Count
        category_count = self.get_category_count_details(product_ids, category, attrib_values, min_price, max_price,
                                                         conversion_rate, website, attrib_set, search, **post)
        res.qcontext.update(category_count=category_count)

        # Tag Count
        tag_count = self.get_tag_count_details(product_ids, category, attrib_values, min_price, max_price,
                                               conversion_rate, website, attrib_set, search, **post)
        res.qcontext.update(tag_count=tag_count)

        if attrib_values:
            attribute_value_count = {}
            for attribute in res.qcontext.get('attributes'):
                attrib_values_list = attrib_values
                modified_list = [sublist for sublist in attrib_values_list if sublist[0] != attribute.id]
                options = self._get_search_options(
                    category=category,
                    attrib_values=modified_list, min_price=min_price,
                    max_price=max_price,
                    conversion_rate=conversion_rate,
                    display_currency=website.currency_id,
                    **post
                )
                fuzzy_search_terms, product_counts, search_products = self._shop_lookup_products(attrib_set, options, post,
                                                                                                 search, website)
                products = search_products.ids
                attribute_counts = self.get_attribute_value_count(products)
                for attribute_id, count in attribute_counts.items():
                    if attribute_id in attribute.value_ids.ids:
                        attribute_value_count[attribute_id] = count
            res.qcontext.update(attribute_value_count=attribute_value_count)
        else:
            options = self._get_search_options(
                category=category,
                attrib_values=attrib_values, min_price=min_price,
                max_price=max_price,
                conversion_rate=conversion_rate,
                display_currency=website.currency_id,
                **post
            )
            fuzzy_search_terms, product_counts, search_products = self._shop_lookup_products(attrib_set, options, post,
                                                                                             search, website)
            # Attribute Value Count
            products = search_products.ids
            attribute_value_count = self.get_attribute_value_count(products)
            res.qcontext.update(attribute_value_count=attribute_value_count)

        # Brand Value Count
        products = product_ids.ids
        brand_value_count = self.get_attribute_value_count(products, is_brand=True)
        res.qcontext.update(brand_value_count=brand_value_count)

        brands = request.env['product.brand'].sudo().search([('website_published', '=', True)])
        if None in brand_value_count.keys() and len(brand_value_count.keys()) > 1:
            res.qcontext.update(brands=brands)

        res.qcontext.update(bins=bins)

        return res
