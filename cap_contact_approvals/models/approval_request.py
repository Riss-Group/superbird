from odoo import models, fields

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    bank_ids = fields.One2many('res.partner.bank','approval_id',string='Banks')
    credit = fields.Float('Total Receivable')
    days_sales_outstanding = fields.Float('Days Sales Outstanding (DSO)')
    use_partner_credit_limit = fields.Boolean('Partner Limit')
    credit_limit = fields.Float(string='Credit Limit', help='Credit limit specific to this partner.',
        groups='account.group_account_invoice,account.group_account_readonly',
        company_dependent=True, copy=False, readonly=False)
