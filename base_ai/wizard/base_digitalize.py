from odoo import models, fields, api
import json
import base64

from odoo.exceptions import UserError


class BaseDigitalize(models.TransientModel):
    _name = 'base.digitalize'
    _description = 'Wizard to upload a file for OCR and update the current record'

    file = fields.Binary(string="File", required=True)
    filename = fields.Char(string="Filename")

    def action_confirm(self):
        self.ensure_one()
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if not active_model or not active_id:
            return

        record = self.env[active_model].browse(active_id)
        data = record.with_context(file_name=self.filename).ocr_prompt(base64.b64decode(self.file))

        fields = data.get('fields', {})
        vals = {}
        for field_name, value in fields.items():
            if field_name in record._fields:
                vals[field_name] = value

        if vals:
            record.write(vals)

        # Optionally, notify the user of success
        self.env.user.notify_info(message="Document digitalized and fields updated successfully.", title="Success")

        return {'type': 'ir.actions.act_window_close'}