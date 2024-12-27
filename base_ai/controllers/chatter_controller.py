from odoo import http
from odoo.http import request
import markdown

class ChatterController(http.Controller):
    @http.route('/ai_chatter/messages', type='json', auth='user')
    def fetch_messages(self, model, id):
        record = request.env[model].browse(id)
        messages = record.ai_message_ids.mapped(lambda m: {
            'id': m.id,
            # If you still want an "author" name to display,
            # you could map the create_uid's name:
            'author': m.create_uid.name if m.role == 'user' else 'Odoo AI',
            'content': markdown.markdown(m.content) if m.content else False,
            'role': m.role,
        })
        return messages

    @http.route('/ai_chatter/post_message', type='json', auth='user')
    def post_message(self, model, id, message):
        record = request.env[model].browse(id)

        response = record.ai_query_prompt(message)
        return {
            'status': 'ok',
            'user_message': message,
            'assistant_response': response,
        }
