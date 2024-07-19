from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger()

class AccountAccountTemplate(models.Model):
    _name = 'account.account.template'
    _description = 'Chart of Accounts (Template)'
    _inherit = ['mail.thread']
    _order = "code, name"
    
    ACCOUNT_TYPE_SELECTION =[
            ("asset_receivable", "Receivable"),
            ("asset_cash", "Bank and Cash"),
            ("asset_current", "Current Assets"),
            ("asset_non_current", "Non-current Assets"),
            ("asset_prepayments", "Prepayments"),
            ("asset_fixed", "Fixed Assets"),
            ("liability_payable", "Payable"),
            ("liability_credit_card", "Credit Card"),
            ("liability_current", "Current Liabilities"),
            ("liability_non_current", "Non-current Liabilities"),
            ("equity", "Equity"),
            ("equity_unaffected", "Current Year Earnings"),
            ("income", "Income"),
            ("income_other", "Other Income"),
            ("expense", "Expenses"),
            ("expense_depreciation", "Depreciation"),
            ("expense_direct_cost", "Cost of Revenue"),
            ("off_balance", "Off-Balance Sheet"),]
    
    INTERNAL_GROUP_SELECTION = [
            ('equity', 'Equity'),
            ('asset', 'Asset'),
            ('liability', 'Liability'),
            ('income', 'Income'),
            ('expense', 'Expense'),
            ('off_balance', 'Off Balance'),]

    code = fields.Char('Account Code', tracking=True)
    name = fields.Char('Name', tracking=True)
    company_ids = fields.Many2many('res.company', tracking=True)
    account_type = fields.Selection(selection=ACCOUNT_TYPE_SELECTION, required=True,)
    internal_group = fields.Selection( selection=INTERNAL_GROUP_SELECTION, string="Internal Group", compute="_compute_internal_group", store=True, precompute=True,)
    tag_ids = fields.Many2many('account.account.tag', 'account_account_template_tag', string='Tags', 
        help="Optional tags you may want to assign for custom reporting")
    deprecated = fields.Boolean(default=False, tracking=True)
    non_trade = fields.Boolean(default=False, help="If set, this account will belong to Non Trade Receivable/Payable in reports and filters.\n\
        If not, this account will belong to Trade Receivable/Payable in reports and filters.")
    currency_id = fields.Many2one('res.currency', string='Account Currency', tracking=True,
        help="Forces all journal items in this account to have a specific currency (i.e. bank journals). If no currency is set, entries can use any currency.")
    reconcile = fields.Boolean('Allow Reconciliation', tracking=True)
    account_lines = fields.One2many('account.account', 'account_template_id', 'Children Accounts')
    child_used = fields.Boolean(compute='_compute_child_used')


    @api.constrains('account_type', 'reconcile')
    def _check_reconcile(self):
        for account in self:
            if account.account_type in ('asset_receivable', 'liability_payable') and not account.reconcile:
                raise ValidationError(_('You cannot have a receivable/payable account that is not reconcilable. (account code: %s)', account.code))

    @api.depends('account_lines')
    def _compute_child_used(self):
        for rec in self:
            accounts = self.env['account.account'].sudo().search([('account_template_id','=',rec.id),('used','=',True)],limit=1 )
            if accounts:
                rec.child_used = True
            else:
                rec.child_used = False

    @api.depends('account_type')
    def _compute_internal_group(self):
        for account in self:
            if account.account_type:
                account.internal_group = 'off_balance' if account.account_type == 'off_balance' else account.account_type.split('_')[0]

    def _get_vals_dict(self,company_id=False):
        self.ensure_one()
        vals = {
            'account_template_id' : self.id,
            'code' : self.code,
            'name' : self.name,
            'account_type': self.account_type,
            'tag_ids': [(6,0,self.tag_ids.ids)],
            'deprecated': self.deprecated,
            'non_trade': self.non_trade,
            'currency_id': self.currency_id.id,
            'reconcile': self.reconcile,            
        }
        if company_id:
            vals.update({'company_id':company_id.id})
        return vals
    
    @api.model_create_multi
    def create(self, vals):
        records = super().create(vals)
        for record in records:
            if self.env.context.get('log_results'):
                _logger.warning(f'***CREATING {record}')
            for company in record.company_ids:
                account_id = self.env['account.account'].sudo().search([
                    ('company_id', '=', company.id),
                    ('name', '=', record.name ),
                    ('code', '=', record.code ),
                ])
                if account_id:
                    account_id.sudo().write(record._get_vals_dict(company))
                else:
                    self.env['account.account'].sudo().create(record._get_vals_dict(company))
        return records

    def write(self, vals):
        res = super().write(vals)
        if self.env.context.get('log_results'):
            _logger.warning(f'***WRITING {res}')
        for record in self:
            for account_id in record.sudo().account_lines:
                account_id.sudo().write(record._get_vals_dict())
            list_company_ids = record.account_lines.mapped('company_id.id')
            company_ids = record.company_ids.filtered(lambda x: x.id not in list_company_ids)
            for company_id in company_ids:
                vals = record._get_vals_dict(company_id)
                self.env['account.account'].sudo().create(vals)
        return res

    def unlink(self):
        for record in self:
            #Odoo by default wont unlink accounts linked to existing entries so no check needs to be added here.
            record.account_lines.unlink()
        return super().unlink()