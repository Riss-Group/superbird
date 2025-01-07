from odoo import models, fields, api

class AccountAccountExpenseDistribution(models.Model):
    _name = 'account.account.expense.distribution'
    _description = 'Expense Distribution'

    account_id = fields.Many2one(comodel_name='account.account',
                                 string="Account",
                                 required=True,
                                 ondelete='cascade')
    account_distribution_id = fields.Many2one(comodel_name='account.account',
                                              string="Distributed Account",
                                              required=True)
    percent_distribution = fields.Integer(string="Percent Distribution",required=True)

    account_type = fields.Selection(
        related='account_id.account_type',
        string="Account Type",
        store=True
    )

