from odoo import models, fields, api
import json

class AccountMove(models.Model):
    _inherit = 'account.move'

    ocr_attachment_id = fields.Many2one('ir.attachment')

    def action_post(self):
        res = super().action_post()
        for rec in self.filtered(lambda i: i.ocr_attachment_id and i.partner_id and i.move_type == 'in_invoice' and not i.partner_id.ocr_template_move_id):
            rec.partner_id.ocr_template_move_id = rec.id
        return res

    def ocr_prompt(self, file_content, extra_instructions=""):
        ir_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        if not self.partner_id:
            file_name = self._context.get('file_name', 'document.pdf')
            ocr_text = self._perform_ocr_or_extraction(file_content, file_name)
            ConfigParam = self.env['ir.config_parameter'].sudo()
            ai_model_id = ConfigParam.get_param('base_ai.ocr_model_id')
            if not ai_model_id:
                raise ValueError("No AI model configuration found. Please configure it in Settings.")

            ai_model = self.env['ai.model'].browse(int(ai_model_id))
            json_structure_str = ir_model.get_json_structure(only_fields=['partner_id'])
            prompt = f"""
            Extract only the partner_id from the document using OCR.
            Return only a valid JSON with the detected partner_id.
            JSON Structure:
            ```json
            {json_structure_str}
            ```
            Digitalized text:
            ```text
            {ocr_text}
            ```
            """
            system_prompt = "You are a helpful assistant."

            assistant_reply = ai_model.ai_prompt(prompt, system_prompt, None, [], ir_model.max_tokens,
                                                 ir_model.temperature)
            partner_data = self.extract_json_from_response(assistant_reply)
            if partner_data.get('partner_id'):
                self.write({'partner_id': partner_data['partner_id']})
                if self.partner_id.extra_instructions:
                    extra_instructions = '\n'.join([extra_instructions, self.partner_id.extra_instructions])
        return super().ocr_prompt(file_content, extra_instructions=extra_instructions)