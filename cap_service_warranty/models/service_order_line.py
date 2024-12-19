# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ServiceOrderLine(models.Model):
    _inherit = 'service.order.line'

    warranty_partner_id = fields.Many2one('res.partner', string='Warranty Partner')
