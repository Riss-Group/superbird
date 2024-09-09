# -*- coding: utf-8 -*-
# from odoo import http


# class CapStockBarcode(http.Controller):
#     @http.route('/cap_stock_barcode/cap_stock_barcode', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cap_stock_barcode/cap_stock_barcode/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cap_stock_barcode.listing', {
#             'root': '/cap_stock_barcode/cap_stock_barcode',
#             'objects': http.request.env['cap_stock_barcode.cap_stock_barcode'].search([]),
#         })

#     @http.route('/cap_stock_barcode/cap_stock_barcode/objects/<model("cap_stock_barcode.cap_stock_barcode"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cap_stock_barcode.object', {
#             'object': obj
#         })

