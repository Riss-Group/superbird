from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OcrModelConfig(models.Model):
    _name = 'ai.model.config'
    _description = 'AI Model Configuration'

    name = fields.Char(string='Name', required=True, help="Descriptive name for the AI model configuration.")
    api_key = fields.Char(string='API Key', required=True)
    model = fields.Char(string='Model', required=True, default='gpt-4o')
    max_tokens = fields.Integer(string='Max Tokens', default=1500)
    temperature = fields.Float(string='Temperature', default=0.0)

    @api.constrains('api_key')
    def _check_api_key(self):
        for record in self:
            if not record.api_key:
                raise ValidationError("API Key is required for the AI model configuration.")