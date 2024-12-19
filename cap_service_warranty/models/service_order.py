# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ServiceOrder(models.Model):
    _inherit = 'service.order'

    def action_clam_warranty(self):
       self.ensure_one()
       service_order_line = self.service_order_line_ids.filtered(lambda x: x.ttype == 'Warranty' and x.warranty_partner_id)
       warranty_partner_ids = service_order_line.mapped('warranty_partner_id')
       for warranty_partner in warranty_partner_ids:
           line_vals = []
           for line in service_order_line.filter(lambda x: x.warranty_partner_id == warranty_partner):
               line_vals += self._get_so_line_product_details(line)
           warranty_clam = self.env['warranty.clam'].create({
               'partner_id': warranty_partner.id
           })


    def _get_so_line_product_details(self, line):
        return {'product_id': line.product_id.id, 'product_uom_qty': line.quantity, 'price_unit': line.unit_price}