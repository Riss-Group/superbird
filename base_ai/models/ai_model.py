# File: ./models/ai_model.py
from pyexpat.errors import messages

from odoo import models, fields, api
from odoo.exceptions import UserError
from openai import OpenAI

class AiModel(models.Model):
    _name = 'ai.model'
    _description = 'AI Model Configuration'

    name = fields.Char(string='Name', required=True)
    api_key = fields.Char(string='API Key', required=True)
    model = fields.Char(string='Model', required=True, default='gpt-4')
    max_tokens = fields.Integer(string='Max Tokens', default=1500)
    temperature = fields.Float(string='Temperature', default=0.0)
    log_count = fields.Integer(string="Log Count", compute="_compute_log_count")
    ai_model_log_ids = fields.One2many('ai.model.log', 'ai_model_id', string='Log')

    @api.depends('ai_model_log_ids')
    def _compute_log_count(self):
        for record in self:
            record.log_count = self.env['ai.model.log'].search_count([('ai_model_id', '=', record.id)])

    def open_logs(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("base_ai.action_ai_model_log")
        action['domain'] = [ ('ai_model_id', '=', self.id)]
        return action

    def ai_prompt(self, prompt, system_prompt=None, image_url=None, max_tokens=None, temperature=None):
        self.ensure_one()
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
        client = OpenAI(api_key=self.api_key)
        content = [{
                        "type": "text",
                        "text": prompt.strip(),
                    }]
        if image_url:
            content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                    })
        messages = [
            {
                "role": "user",
                "content": content
            }
        ]
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            # Create a log entry after the prompt is sent and response is received
            self.env['ai.model.log'].create({
                'prompt_query': prompt,
                'prompt_response': response.choices[0].message.content,
                'ai_model_id': self.id,
            })
            return response.choices[0].message.content
        except Exception as e:
            raise UserError(f"Error calling the OpenAI API: {e}")
