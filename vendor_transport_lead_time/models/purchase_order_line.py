# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from operator import index

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    supplier_date_planned = fields.Datetime(string="Supplier Scheduled Date", compute="_compute_supplier_date_planned",
                                            store=True, index=True)
    report_date_planned = fields.Datetime(
        string="Date planned (used by report)",
        compute="_compute_report_date_planned",
    )

    @api.depends('date_planned', 'product_id', 'product_qty', 'product_uom', 'company_id')
    def _compute_supplier_date_planned(self):
        for line in self:
            line.supplier_date_planned = line._get_supplier_date_planned()

    def _get_supplier_date_planned(self):
        """Return the datetime value to use as Supplier Schedule Date
        (``supplier_date_planned``) for the current PO line.

        :rtype: datetime
        :return: desired Supplier Schedule Date for the PO line or False
        """
        self.ensure_one()
        if not self.product_id or not self.date_planned:
            return False
        # When coming from an onchange, the 'order_id.date_order' could be False
        date_order = (
            self.order_id.date_order
            and self.order_id.date_order.date()
            or fields.Date.context_today(self),
        )
        params = self._get_select_sellers_params()
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=date_order,
            uom_id=self.product_uom,
            params=params,
        )
        if not seller:
            return False
        return fields.Datetime.subtract(self.date_planned, days=seller.delay)

    def _compute_report_date_planned(self):
        for line in self:
            if line.date_planned and line.supplier_date_planned:
                line.report_date_planned = min(
                    line.date_planned, line.supplier_date_planned
                )
            else:
                line.report_date_planned = line.date_planned
