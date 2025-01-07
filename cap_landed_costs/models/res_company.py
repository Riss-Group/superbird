from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'


    auto_landed_cost_account_id = fields.Many2one('account.account', domain="[('deprecated', '=', False)]")