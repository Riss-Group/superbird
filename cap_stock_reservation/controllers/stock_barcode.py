# -*- coding: utf-8 -*-


from odoo import http, _
from odoo.http import request



class StockBarcodeController(http.Controller):

    def _get_allowed_company_ids(self):
        cids = request.httprequest.cookies.get('cids', str(request.env.user.company_id.id))
        return [int(cid) for cid in cids.split(',')]

    @http.route('/stock_barcode/reassign_moves', type='json', auth='user')
    def reassign_moves(self, model, res_id):
        if not res_id:
            target_pick = request.env[model].with_context(allowed_company_ids=self._get_allowed_company_ids())
        else:
            target_pick = request.env[model].browse(res_id).with_context(allowed_company_ids=self._get_allowed_company_ids())

        if target_pick.picking_type_id.bypass_reservation and all(m.state == 'assigned' for m in target_pick.move_ids):
            products = target_pick.move_ids.mapped('product_id')
            all_product_reserved_moves = request.env['stock.move'].search([('state','in', ['assigned', 'partially_available']),('product_id','in',products.ids),
                                                                        ('picking_type_id','=',target_pick.picking_type_id.id)])
            all_product_reserved_moves.mapped('picking_id').do_unreserve()
            request.env.cr.commit()
            # after removing all the reservations, reassign it back
            target_pick.action_assign()

            picks = all_product_reserved_moves.filtered(lambda m:m.picking_id != target_pick).mapped('picking_id')
            for pick in picks:
                try:
                    pick.action_assign()
                except:
                    pass

