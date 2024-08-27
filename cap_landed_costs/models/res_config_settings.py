from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    auto_landed_cost_account_id = fields.Many2one('account.account', related='company_id.auto_landed_cost_account_id', domain="[('deprecated', '=', False)]", readonly=False, store=True)