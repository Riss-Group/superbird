# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'


    def action_open_dirty_cores_return(self):
        # the dirty cores returns are already created in the system and only need to be batched and reserved
        action =  {
            'name': 'Dirty Cores Return',
            'type': 'ir.actions.act_window',
            'res_model': 'dirty_core.return',
            'view_mode': 'form',
            'context': {
                'default_model': 'sale.order',
                'default_partner_id': self.partner_id.id,
                'default_ticket_id': self.id,
            },
            'target': 'new',
        }
        return action
