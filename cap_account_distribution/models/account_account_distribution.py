from odoo import models, fields, api

class AccountAccountDistribution(models.Model):
    _name = 'account.account.distribution'
    _description = 'Admin Distribution'

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

