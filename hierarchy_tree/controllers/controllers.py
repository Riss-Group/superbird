# -*- coding: utf-8 -*-
# from odoo import http


# class HierarchTree(http.Controller):
#     @http.route('/hierarch_tree/hierarch_tree', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hierarch_tree/hierarch_tree/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hierarch_tree.listing', {
#             'root': '/hierarch_tree/hierarch_tree',
#             'objects': http.request.env['hierarch_tree.hierarch_tree'].search([]),
#         })

#     @http.route('/hierarch_tree/hierarch_tree/objects/<model("hierarch_tree.hierarch_tree"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hierarch_tree.object', {
#             'object': obj
#         })

