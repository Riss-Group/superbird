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

        request_args = request.httprequest.args
        post.update(request_args=request_args.getlist('attribute_value', None))

        mutable_data = request_args.to_dict(flat=False)  # flat=False retains multiple values for the same key

        if 'attribute_value' in mutable_data:
            mutable_data['attribute_value'] = [
                value for value in mutable_data['attribute_value'] if value and not value.startswith('0')
            ]

        request.httprequest.args = ImmutableOrderedMultiDict(mutable_data)
        
        Category = request.env['product.public.category']
        if category:
            category_item = Category.search([('id', '=', int(category))], limit=1)
            if not category_item or not category_item.can_access_from_current_website():
                raise NotFound()
            category_children = Category.search([('parent_id', '=', category_item.id)])
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
            categories = Categories.search([])
            category_products = []
            for category in categories:
                if not category.parent_id and category.child_id:
                    child_categories = category.child_id
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

        return res