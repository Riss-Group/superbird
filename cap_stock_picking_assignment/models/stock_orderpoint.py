from odoo import  fields, models, api
from collections import defaultdict
from odoo.tools import float_compare, float_is_zero, frozendict, split_every


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    incoming_qty = fields.Float('Incoming Qty', readonly=True, compute='_compute_qty', digits='Product Unit of Measure')
    outgoing_qty = fields.Float('Outgoing Qty', readonly=True, compute='_compute_qty', digits='Product Unit of Measure')

    def _compute_qty(self):
        super(StockWarehouseOrderpoint, self)._compute_qty()
        orderpoints_contexts = defaultdict(lambda: self.env['stock.warehouse.orderpoint'])
        for orderpoint in self:
            if not orderpoint.product_id or not orderpoint.location_id:
                orderpoint.incoming_qty = False
                orderpoint.outgoing_qty = False
                continue
            orderpoint_context = orderpoint._get_product_context()
            product_context = frozendict({**orderpoint_context})
            orderpoints_contexts[product_context] |= orderpoint
        for orderpoint_context, orderpoints_by_context in orderpoints_contexts.items():
            products_qty = {
                p['id']: p for p in orderpoints_by_context.product_id.with_context(orderpoint_context).read(['incoming_qty', 'outgoing_qty'])
            }
            products_qty_in_progress = orderpoints_by_context._quantity_in_progress()
            for orderpoint in orderpoints_by_context:
                orderpoint.incoming_qty = products_qty[orderpoint.product_id.id]['incoming_qty']
                orderpoint.outgoing_qty = products_qty[orderpoint.product_id.id]['outgoing_qty'] + products_qty_in_progress[orderpoint.id]