
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    supplier_date_planned = fields.Datetime(string="Supplier Scheduled Date", compute="_compute_supplier_date_planned",
                                            store=True, index=True)

    @api.depends('order_line.supplier_date_planned')
    def _compute_supplier_date_planned(self):
        """ supplier_date_planned = the earliest supplier_date_planned across all order lines. """
        for order in self:
            dates_list = order.order_line.filtered(lambda x: not x.display_type and x.supplier_date_planned).mapped(
                'supplier_date_planned')
            if dates_list:
                order.supplier_date_planned = min(dates_list)
            else:
                order.supplier_date_planned = False