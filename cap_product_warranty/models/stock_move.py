# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta



class StockMove(models.Model):
    _inherit = 'stock.move'

    warranty_expiration_date = fields.Date(string="Product Warranty Expiration Date", default=False, copy=False)

    def _action_done(self, cancel_backorder=False):
        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
        for move in res.filtered(lambda m: m.picking_code == 'incoming'):
            product = move.product_id
            if product.warranty_type == 'day':
                move.warranty_expiration_date = fields.Date.today() + relativedelta(days=product.warranty)
            elif product.warranty_type == 'week':
                move.warranty_expiration_date = fields.Date.today() + relativedelta(weeks=product.warranty)
            elif product.warranty_type == 'month':
                move.warranty_expiration_date = fields.Date.today() + relativedelta(months=product.warranty)
            elif product.warranty_type == 'year':
                move.warranty_expiration_date = fields.Date.today() + relativedelta(years=product.warranty)
