from odoo import models, fields


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    automate_interco_invoice = fields.Boolean(
        string="Automate Intercompany Invoice"
    )
    interco_partner_id = fields.Many2one(
        "res.partner",
        string="Intercompany Partner",
        domain=[("is_company", "=", True)],
    )
