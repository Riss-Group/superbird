
from odoo import api, fields, Command, models, _


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position',
                                         domain="[('company_id', '=', company_id)]")

    def _get_default_expense_sheet_values(self):
        res = super(HrExpense, self)._get_default_expense_sheet_values()
        statement_line_id = self.env['account.bank.statement.line'].sudo().search([('expense_id', '=', self.id)])
        if statement_line_id and statement_line_id.journal_id and statement_line_id.journal_id.outbound_payment_method_line_ids:
            for values in res:
                values.update({'payment_method_line_id': statement_line_id.journal_id.outbound_payment_method_line_ids[:1].id})
        return res

    @api.depends('product_id', 'company_id', 'fiscal_position_id')
    def _compute_tax_ids(self):
        for _expense in self:
            expense = _expense.with_company(_expense.company_id)
            # taxes only from the same company
            taxes = expense.product_id.supplier_taxes_id.filtered_domain(self.env['account.tax']._check_company_domain(expense.company_id))
            if expense.fiscal_position_id:
                taxes = expense.fiscal_position_id.map_tax(taxes)
            expense.tax_ids = taxes
