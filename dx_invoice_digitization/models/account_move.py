
from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'account.move'

    def action_show_digitalize_wizard(self):
        return {
            'name': 'Digitalize Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'invoice.digitalize',
            'view_mode': 'form',
            'context': {'active_ids': self.ids, 'active_model': 'account.move'},
            'view_id': self.env.ref('dx_invoice_digitization.view_invoice_digitalize_form').id,
            'target': 'new',
        }
