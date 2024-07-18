from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def open_move(self):
        if self.id:
            return {
            'name': _('Journal Entry'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
        }