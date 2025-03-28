# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ServiceOrderLine(models.Model):
    _inherit = 'service.order.line'

    warranty_partner_id = fields.Many2one('res.partner', string='Warranty Partner')
    warranty_claim_line_ids = fields.One2many('warranty.claim.line', 'service_order_line_id')

    @api.onchange('warranty_partner_id')
    def onchange_warranty_partner_id(self):
        for rec in self:
            rec.bill_to_partner_id = rec.warranty_partner_id
