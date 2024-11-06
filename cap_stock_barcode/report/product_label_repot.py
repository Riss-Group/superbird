# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import _, models



class ReportProductLabel(models.AbstractModel):
    _inherit = 'report.stock.label_product_product_view'

    def _get_report_values(self, docids, data):
        active_model = self.env.context.get("active_model")
        if active_model :
            data['active_model'] = 'product.product'
        return super(ReportProductLabel, self)._get_report_values(docids,data)