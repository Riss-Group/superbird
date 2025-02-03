
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[('revised', 'Revised')])
    quote_name = fields.Char(string="Quote Name")

    def _prepare_revision_data(self, new_revision):
        vals = super()._prepare_revision_data(new_revision)
        vals.update({"state": "revised"})
        return vals

    def copy_revision_with_context(self):
        res = super().copy_revision_with_context()
        self.action_copy_chatter(res)
        return res

    def action_copy_chatter(self, revised_id):
        self.ensure_one()
        # Copy messages
        messages = self.env['mail.message'].search([('res_id', '=', self.id), ('model', '=', self._name),], order='create_date')
        for message in messages:
            tracking_values = self.env['mail.tracking.value'].search([('mail_message_id', '=', message.id)], order='create_date')
            new_message_id = message.copy({'res_id': revised_id.id, 'model': self._name,})
            if tracking_values:
                for tracking in tracking_values:
                    tracking.copy({'mail_message_id': new_message_id.id})

        # Move attachments
        Attachment = self.env['ir.attachment']
        attachments = Attachment.search([('res_id', '=', self.id), ('res_model', '=', self._name),], order='create_date')
        for attachment in attachments:
            attachment.write({'res_id': revised_id.id, 'res_model': self._name,})
