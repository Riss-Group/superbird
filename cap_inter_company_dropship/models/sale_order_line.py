# -*- coding: utf-8 -*-

from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'



    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        routes = values.get('route_ids')
        if routes and any(r.dropship_default_company for r in routes):
            partner = routes.filtered(lambda l: l.dropship_default_company).dropship_default_company.partner_id
            requisition = self.env['purchase.requisition']
            values.update({
                'supplierinfo_id': SupplierInfo(partner, requisition),
            })

        return values

class SupplierInfo:
    def __init__(self, partner, requisition):
        # this only added to bypass the product supplierinfo_id table
        self.partner_id = partner
        self.delay = 1
        self.price = 1
        self.min_qty = 1
        self.warranty_return_partner = 'company'
        self.purchase_requisition_id = requisition
