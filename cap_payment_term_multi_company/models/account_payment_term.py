# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountPaymentTerm(models.Model):
    _inherit = ["multi.company.abstract", "account.payment.term"]
    _name = "account.payment.term"

    company_ids = fields.Many2many("res.company",
        relation="account_payment_term_company_rel",  # Unique relation table name
        string="Companies",
    )

