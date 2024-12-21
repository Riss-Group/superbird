# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ServiceOrder(models.Model):
    _inherit = 'service.order'

    warranty_claim_ids = fields.One2many('warranty.claim', 'service_order_id', string="Warranty Claim")

    def action_claim_warranty(self):
       self.ensure_one()
       service_order_line = self.service_order_lines.filtered(lambda x: x.ttype == 'Warranty' and x.warranty_partner_id)
       warranty_partner_ids = service_order_line.mapped('warranty_partner_id')
       for warranty_partner in warranty_partner_ids:
           line_vals = []
           for line in service_order_line.filtered(lambda x: x.warranty_partner_id == warranty_partner):
               line_vals += self._get_so_line_product_details(line)
               line_vals += self._get_so_line_labor_details(line)

           print("line_vals ::: ",line_vals)
           warranty_claim = self.env['warranty.claim'].create({
               'partner_id': warranty_partner.id,
               'warranty_claim_line_ids': line_vals,
               'service_order_id': self.id
           })
           print("warranty_claim :: ",warranty_claim)

    def _get_so_line_product_details(self, line):
        so_line_vals = []
        for so_line_product_id in line.service_order_line_product_ids:
            vals = {
                'product_id': so_line_product_id.product_id.id,
                'quantity': so_line_product_id.quantity,
                'unit_price': so_line_product_id.unit_price,
                'claim_for': 'product',
                'service_order_line_id': line.id
            }
            so_line_vals.append((0, 0, vals))
        return so_line_vals

    def _get_so_line_labor_details(self, line):
        so_line_vals = []
        for so_line_service_id in line.service_order_line_service_ids:
            vals = {
                'product_id': so_line_service_id.product_id.id,
                'quantity': so_line_service_id.quantity,
                'unit_price': so_line_service_id.unit_price,
                'claim_for': 'labor',
                'service_order_line_id': line.id
            }
            so_line_vals.append((0, 0, vals))
        return so_line_vals

    def action_stat_button_warranty_claim(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Warranty Claims',
            'view_mode': 'tree,form',
            'res_model': 'warranty.claim',
            'context': {
            },
            'domain': [('id', 'in', self.warranty_claim_ids.ids)]
        }
