import odoo.exceptions
from odoo import models, fields, api
from odoo.exceptions import UserError

class BaseAiQuery(models.TransientModel):
    _name = 'base.ai.query'
    _description = 'AI Query Wizard'

    prompt_query = fields.Text(string="Query", required=True)
    prompt_response = fields.Text(string="Response", readonly=True)


    def action_send_query(self):
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if not self.prompt_query:
            raise UserError("Please enter a query before sending.")
        record = self.env[active_model].browse(active_id)
        response = record.ai_query_prompt(self.prompt_query)
        self.prompt_response = response
        raise odoo.exceptions.UserError(response)