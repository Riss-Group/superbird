# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    tax_exemption_fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string="Tax Exemption Fiscal Position",
        help="Default fiscal position used for tax exemption contact.",
        check_company=True,
    )
