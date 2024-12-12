
from odoo import models, fields, api

class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def ocr_enabled(self):
        return self.env['ir.model'].search([('name', '=', self._name)]).ocr_enabled

    @api.model
    def ai_exposed_fields(self):
        return self.env['ir.model'].search([('name', '=', self._name)]).ai_exposed_fields.mapped('name')

    @api.model
    def ai_obfuscated_fields(self):
        return self.env['ir.model'].search([('name', '=', self._name)]).ai_obfuscated_fields.mapped('name')

    def action_show_digitalize_wizard(self):
        return {
            'name': 'Digitalize Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'base.digitalize',
            'view_mode': 'form',
            'context': {'active_ids': self.ids, 'active_model': self._name},
            'view_id': self.env.ref('base_ai.view_base_digitalize_form').id,
            'target': 'new',
        }
