from odoo import  models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__) 


class AccountAccount(models.Model):
    _inherit = 'account.account'   


    account_template_id = fields.Many2one(comodel_name='account.account.template', string='Template Account')

    def action_open_coa(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Accounts',
            'view_mode': 'form',
            'res_model': 'account.account',
            'res_id': self.id
        }