# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    expense_id = fields.Many2one('hr.expense', string='Expense')
    journal_employee_user_id = fields.Many2one('res.users', related='journal_id.employee_id.user_id')

    def create_expense_action(self):
        if not self.journal_id.employee_id:
            raise ValidationError(_('Please define an employee on the journal'))
        expense_dict = {'name': self.payment_ref, 'employee_id': self.journal_id.employee_id.id, 'date': self.date,
                        'total_amount_currency': abs(self.amount), 'currency_id': self.currency_id.id,
                        'company_id': self.company_id.id, 'product_id': self.company_id.expense_product_id.id,
                        'payment_mode': 'company_account'}
        expense_id = self.env['hr.expense'].create(expense_dict)
        self.sudo().expense_id = expense_id

    def view_expense(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.expense',
            'view_mode': 'form',
            'res_id': self.expense_id.id,
        }
