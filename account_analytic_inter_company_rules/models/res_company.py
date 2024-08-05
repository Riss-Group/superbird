# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    account_interco_revenue_account_id = fields.Many2one(
        "account.account",
        string="Default Revenue Account for Intercompany Transactions",
    )
