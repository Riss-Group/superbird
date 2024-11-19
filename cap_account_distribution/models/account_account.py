from odoo import models, fields
from odoo.exceptions import UserError

class AccountAccount(models.Model):
    _inherit = 'account.account'

    account_distribution_lines = fields.One2many(comodel_name='account.account.distribution',
                                                 inverse_name='account_id',
                                                 string='Admin Distribution Lines')
    account_expense_distribution_lines = fields.One2many(comodel_name='account.account.expense.distribution',
                                                 inverse_name='account_id',
                                                 string='Expense Distribution Lines')
    def _check_percent_sum(self, lines):
        percent_total = sum(self.account_distribution_lines.mapped('percent_distribution'))
        if percent_total != 100 and percent_total > 0:
            err = f"Redistribution of Lines need to sum to 100%.\nPlease reconfigure the lines or discard changes.\nCurrent Total Percentage: {percent_total}"
            raise UserError(err)

    def write(self, vals):
        res = super(AccountAccount, self).write(vals)
        print(f"\n\nADLines: {vals.get('account_distribution_lines')}\n\n")
        print(f"\n\nAEDLines: {vals.get('account_expense_distribution_lines')}\n\n")
        adlines = vals.get('account_distribution_lines')
        aedlines = vals.get('account_expense_distribution_lines')
        if adlines:
            self._check_percent_sum(self.account_distribution_lines)
        if aedlines:
            self._check_percent_sum(self.account_expense_distribution_lines)
        return res

