import re
from ast import literal_eval

from odoo import models, api, fields
import os
import io
import logging
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import base64
import requests
import boto3
import json
_logger = logging.getLogger(__name__)

class Base(models.AbstractModel):
    _inherit = "base"

    ai_message_ids = fields.One2many(
        'ai.message',
        'res_id',
        string='AI Chat Log',
        domain=lambda self: [
            ('res_model', '=', self._name),
            ('create_uid', '=', self.env.user.id)
        ],
    )

    def show_ocr_button(self):
        ir_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        domain = literal_eval(ir_model.ai_exposed_domain) if ir_model.ai_exposed_domain else []
        domain += [('id', 'in', self.ids)]
        return ir_model.ocr_enabled and self.search_count(domain)

    def show_ai_button(self):
        ir_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        domain = literal_eval(ir_model.ai_exposed_domain) if ir_model.ai_exposed_domain else []
        domain += [('id', 'in', self.ids)]
        return ir_model.ai_query_enabled and self.search_count(domain)

    @api.model
    def ai_exposed_fields(self):
        ir_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        return ir_model.ai_exposed_field_ids if ir_model else []

    @api.model
    def ai_obfuscated_fields(self):
        ir_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        return ir_model.ai_obfuscated_field_ids.mapped('name') if ir_model else []

    def action_show_digitalize_wizard(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("base_ai.base_digitalize_action")
        action['context'] = {'active_id': self.id, 'active_model': self._name}
        return action

    def action_show_ai_query_wizard(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("base_ai.base_ai_query_action")
        action['context'] = {'active_id': self.id, 'active_model': self._name}
        return action

    def ai_query_prompt(self, prompt):
        self.ensure_one()
        ir_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
          # Gather all previous messages
        previous_messages = []

        for message in self.ai_message_ids:
            previous_messages.append({
                "role": message.role,
                "content": message.content
            })
        extra_instructions = ir_model.extra_instructions_ai or ""
        json_structure_str = json.dumps(self._convert_to_dict(), default=str, indent=2)
        ConfigParam = self.env['ir.config_parameter'].sudo()
        ai_model_id = ConfigParam.get_param('base_ai.ocr_model_id')
        if not ai_model_id:
            raise ValueError("No AI model configuration found. Please configure it in Settings.")

        ai_model = self.env['ai.model'].browse(int(ai_model_id))
        final_prompt = f"""
{prompt}

The record itself is:
```json
{json_structure_str}
```
Extra Instructions:
```json
{extra_instructions}
```
"""
        response = ai_model.ai_prompt(final_prompt, None, None, previous_messages, ir_model.max_tokens, ir_model.temperature)
        self.env['ai.message'].create({
            'res_id': self.id,
            'res_model': self._name,
            'role': 'user',
            'content': prompt,
        })
        self.env['ai.message'].create({
            'res_id': self.id,
            'res_model': self._name,
            'role': 'assistant',
            'content': response,
        })
        return response

    @api.model
    def ocr_prompt(self, file_content, extra_instructions=""):
        ir_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        extra_instructions = '\n'.join([ir_model.extra_instructions_ocr, extra_instructions]) if ir_model.extra_instructions_ocr and extra_instructions else ""
        json_structure_str = ir_model.get_json_structure()

        # file_name should be in context
        file_name = self._context.get('file_name', 'document.pdf')
        ocr_text = self._perform_ocr_or_extraction(file_content, file_name)

        ConfigParam = self.env['ir.config_parameter'].sudo()
        ai_model_id = ConfigParam.get_param('base_ai.ocr_model_id')
        if not ai_model_id:
            raise ValueError("No AI model configuration found. Please configure it in Settings.")

        ai_model = self.env['ai.model'].browse(int(ai_model_id))

        prompt = f"""
Below is digitalized text from a document. Please extract the information according to the JSON structure provided.
Return only the JSON dictionary with the extracted values without any additional formatting. If a field cannot be found, don't return it.
If a field is many2one, return the best id from possible_values. If it's many2many return a list of best ids from possible_values.

**Important:** 
- Return **only** the JSON dictionary.
- Do **not** include any markdown formatting, explanations, or additional text.
- Ensure that the JSON is valid and properly formatted.

JSON Structure:
```json
{json_structure_str}
```
Digitalized text:
```text
{ocr_text}
```
Extra Instructions:
```text
{extra_instructions}
```
"""
        system_prompt = "You are a helpful assistant."

        assistant_reply = ai_model.ai_prompt(prompt, system_prompt, None, [], ir_model.max_tokens, ir_model.temperature)
        return self.extract_json_from_response(assistant_reply)

    def _perform_ocr_or_extraction(self, file_content, file_name):
        extension = os.path.splitext(file_name)[1].lower()
        file_type = 'pdf' if extension == '.pdf' else 'image'

        ConfigParam = self.env['ir.config_parameter'].sudo()
        ocr_service = ConfigParam.get_param('base_ai.ocr_service', 'pytesseract')

        if file_type == 'pdf':
            images = self._pdf_to_images(file_content)
            extracted_text_pages = []
            for img in images:
                extracted_text_pages.append(self._ocr_image_with_fallback(img, ocr_service))
            return "\n".join(extracted_text_pages)
        else:
            image = Image.open(io.BytesIO(file_content))
            return self._ocr_image_with_fallback(image, ocr_service)

    def _pdf_to_images(self, file_content):
        try:
            return convert_from_bytes(file_content)
        except Exception as e:
            raise ValueError(f"Error converting PDF to images: {e}")

    def _ocr_image_with_fallback(self, image, ocr_service):
        if ocr_service == 'pytesseract':
            return self._ocr_image_pytesseract(image)
        elif ocr_service == 'google_vision':
            try:
                return self._ocr_image_google_vision(image)
            except Exception as e:
                _logger.error("Google Vision OCR failed: %s. Falling back to pytesseract.", e)
                return self._ocr_image_pytesseract(image)
        elif ocr_service == 'aws_textract':
            try:
                return self._ocr_image_aws_textract(image)
            except Exception as e:
                _logger.error("AWS Textract OCR failed: %s. Falling back to pytesseract.", e)
                return self._ocr_image_pytesseract(image)
        elif ocr_service == 'openai_vision':
            try:
                return self._ocr_image_openai_vision(image)
            except Exception as e:
                _logger.error("OpenAI Vision OCR failed: %s. Falling back to pytesseract.", e)
                return self._ocr_image_pytesseract(image)
        else:
            return self._ocr_image_pytesseract(image)

    def _ocr_image_pytesseract(self, image):
        text = pytesseract.image_to_string(image)
        return text.strip()

    def _ocr_image_google_vision(self, image):
        ConfigParam = self.env['ir.config_parameter'].sudo()
        api_key = ConfigParam.get_param('base_ai.google_vision_api_key')
        if not api_key:
            raise ValueError("Google Vision API key not configured.")

        # Convert image to base64
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        content = base64.b64encode(img_bytes.getvalue()).decode('utf-8')

        url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
        payload = {
            "requests": [
                {
                    "image": {"content": content},
                    "features": [{"type": "TEXT_DETECTION"}]
                }
            ]
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise ValueError(f"Google Vision API error: {response.text}")

        resp_json = response.json()
        try:
            text = resp_json['responses'][0]['fullTextAnnotation']['text']
        except KeyError:
            text = ""

        return text.strip()

    def _ocr_image_aws_textract(self, image):
        ConfigParam = self.env['ir.config_parameter'].sudo()
        aws_access_key_id = ConfigParam.get_param('base_ai.aws_access_key_id')
        aws_secret_access_key = ConfigParam.get_param('base_ai.aws_secret_access_key')
        aws_region = ConfigParam.get_param('base_ai.aws_region', 'us-east-1')

        if not (aws_access_key_id and aws_secret_access_key):
            raise ValueError("AWS credentials not configured for Textract.")

        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        content = img_bytes.getvalue()

        client = boto3.client(
            'textract',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        response = client.detect_document_text(Document={'Bytes': content})

        blocks = response.get('Blocks', [])
        lines = [block['Text'] for block in blocks if block['BlockType'] == 'LINE']
        return "\n".join(lines).strip()

    def _ocr_image_openai_vision(self, image):
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        base64_image = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
        image_url = f"data:image/jpeg;base64,{base64_image}"
        prompt = "Extract the text from this image, ensuring all text is captured accurately. Do not include any markdown or code formatting."
        ConfigParam = self.env['ir.config_parameter'].sudo()
        ai_model_id = ConfigParam.get_param('base_ai.ocr_model_id')
        if not ai_model_id:
            raise ValueError("No AI model configuration found. Please configure it in Settings.")

        ai_model = self.env['ai.model'].browse(int(ai_model_id))
        # Hypothetical model
        response = ai_model.ai_prompt(prompt, None, image_url)
        return response

    def _convert_to_dict(self, depth=0):
        ir_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        max_depth = ir_model.max_depth or 2
        if depth > max_depth:
            return {}
        self.ensure_one()

        # Get the exposed field names
        exposed_fields = self.ai_exposed_fields()  # Use the existing ai_exposed_fields method

        # Build a dictionary of exposed fields and their values
        exposed_fields_data = {
            'id': self.id,
            'display_name': self.display_name
        }
        for field in exposed_fields:
            if self[field.name]:
                if field.ttype == 'many2one':
                    field_value = self[field.name]._convert_to_dict(depth=depth+1)
                elif field.ttype in ('one2many', 'many2many'):
                    field_value = [x._convert_to_dict(depth=depth+1) for x in self[field.name]]
                else:
                    field_value = self[field.name]
                exposed_fields_data[field.name] = {'field_description': field.field_description, 'value': field_value}

        # Return the exposed fields as a JSON string
        return exposed_fields_data

    @api.model
    def extract_json_from_response(self, response):
        patterns = [
            r'```json\s*(\{.*\})\s*```',  # ```json { ... } ```
            r'```(\{.*\})```',  # ```{ ... }```
            r'(\{.*\})',  # { ... }
        ]

        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                json_content = match.group(1)
                try:
                    return json.loads(json_content)
                except json.JSONDecodeError:
                    continue

        raise ValueError("No valid JSON object found in the response.")