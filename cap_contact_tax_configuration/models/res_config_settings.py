from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tax_exemption_fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string="Tax Exemption Fiscal Position",
        help="Default fiscal position used for tax exemption contact.",
        check_company=True,
    )