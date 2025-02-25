# -*- coding: utf-8 -*-
from odoo import models, fields, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    tax_exemption_fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string="Tax Exemption Fiscal Position",
        help="Default fiscal position used for tax exemption contact.")
    exemption_notification_user_ids = fields.Many2many(
        'res.users',
        string="Exemption Notification Users",
        help="Select users to receive exemption certificate expiration notifications."
    )
