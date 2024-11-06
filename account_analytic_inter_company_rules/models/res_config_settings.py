from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    account_interco_revenue_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Default Revenue Account for Intercompany Transactions",
        readonly=False,
        related="company_id.account_interco_revenue_account_id",
        domain=(
            "[('company_id', '=', company_id), ('account_type', '=',"
            " 'income')]"
        ),
        help=(
            "This account will be used by default as the revenue account for"
            " intercompany transactions."
        ),
    )
