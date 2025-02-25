# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tax_exemption_fiscal_position_id = fields.Many2one(related='company_id.tax_exemption_fiscal_position_id',
                                                       readonly=False)
    exemption_notification_user_ids = fields.Many2many(
        'res.users',
        string="Exemption Notification Users",
        related="company_id.exemption_notification_user_ids",
        readonly=False,
        help="Select users to receive exemption certificate expiration notifications."
    )
