from odoo import models, fields, api

class AiModelLog(models.Model):
    _name = 'ai.model.log'
    _description = 'AI Model Log'
    _order = 'prompt_date desc'

    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user, readonly=True)
    prompt_date = fields.Datetime(string='Prompt Date', required=True, default=fields.Datetime.now, readonly=True)
    prompt_query = fields.Text(string='Prompt Query', required=True, readonly=True)
    prompt_response = fields.Text(string='Prompt Response', required=True, readonly=True)
    ai_model_id = fields.Many2one('ai.model', string='AI Model', required=True, readonly=True)

    @api.depends('prompt_date', 'user_id', 'ai_model_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.prompt_date} - {record.user_id.name} ({record.ai_model_id.name if record.ai_model_id else 'Unknown Model'})"

