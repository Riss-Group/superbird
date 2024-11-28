# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def create_expense_action(self):
        if not self.journal_id.employee_id:
            raise ValidationError(_('Please define an employee on the journal'))
        expense_dict = {'name': self.payment_ref, 'employee_id': self.journal_id.employee_id.id, 'date': self.date,
                        'total_amount_currency': abs(self.amount), 'currency_id': self.currency_id.id,
                        'company_id': self.company_id.id}
        self.env['hr.expense'].create(expense_dict)
