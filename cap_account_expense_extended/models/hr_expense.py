
from odoo import api, fields, Command, models, _


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    def _get_default_expense_sheet_values(self):
        res = super(HrExpense, self)._get_default_expense_sheet_values()
        statement_line_id = self.env['account.bank.statement.line'].sudo().search([('expense_id', '=', self.id)])
        if statement_line_id and statement_line_id.journal_id and statement_line_id.journal_id.outbound_payment_method_line_ids:
            for values in res:
                values.update({'payment_method_line_id': statement_line_id.journal_id.outbound_payment_method_line_ids[:1].id})
        return res