# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    employee_id = fields.Many2one('hr.employee', string='Employee', company_dependent=True)