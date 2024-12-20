import re
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
from openai import OpenAI
import json

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class Base(models.AbstractModel):
    _inherit = "base"

    show_ocr_button = fields.Boolean(compute="_compute_show_ocr_button")

    def _compute_show_ocr_button(self):
        for rec in self:
            rec.show_ocr_button = rec.ocr_enabled() if hasattr(rec, 'ocr_enabled') else False

    @api.model
    def ocr_enabled(self):
        ir_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        if not ir_model:
            return False
        return ir_model.ocr_enabled

    @api.model
    def ai_exposed_fields(self):
        ir_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        return ir_model.ai_exposed_field_ids.mapped('name') if ir_model else []

    @api.model
    def ai_obfuscated_fields(self):
        ir_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        return ir_model.ai_obfuscated_field_ids.mapped('name') if ir_model else []

    def action_show_digitalize_wizard(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("base_ai.base_digitalize_action")
        action['context'] = {'active_id': self.id, 'active_model': self._name}
        return action

    @api.model
    def ocr_prompt(self, file_content):
        ir_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        if not ir_model:
            raise ValueError(f"No ir.model record found for model {self._name}")

        json_structure_str = ir_model.get_json_structure()

        # file_name should be in context
        file_name = self._context.get('file_name', 'document.pdf')
        ocr_text = self._perform_ocr_or_extraction(file_content, file_name)

        ConfigParam = self.env['ir.config_parameter'].sudo()
        ai_model_id = ConfigParam.get_param('base_ai.ocr_model_id')
        if not ai_model_id:
            raise ValueError("No AI model configuration found. Please configure it in Settings.")

        ai_model = self.env['ai.model.config'].browse(int(ai_model_id))
        client = OpenAI(api_key=ai_model.api_key)
        if not ai_model.exists():
            raise ValueError("Configured AI model record does not exist.")


        max_tokens = ir_model.max_tokens or ai_model.max_tokens
        temperature = ir_model.temperature if (ir_model.temperature or ir_model.temperature == 0.0) else ai_model.temperature

        prompt = f"""
Below is digitalized text from a document. Please extract the information according to the JSON structure provided.
Return only the JSON dictionary with the extracted values without any additional formatting. If a field cannot be found, set it to False.
If a field has possible_values, Use odoo's fields.Commands to replace the existing values with the id of the best one if it's a many2one, otherwise the list of best ids if it's many2many

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
"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt.strip()},
        ]

        try:
            response = client.chat.completions.create(model=ai_model.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature)
        except Exception as e:
            raise UserError(f"Error calling the OpenAI API: {e}")

        assistant_reply = response.choices[0].message.content.strip()
        return extract_json_from_response(assistant_reply)

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
        # Hypothetical integration with an OpenAI Vision-capable model.
        # This code is inspired by your snippet.
        # Adjust the model and message format as per actual supported features.

        # Ensure openai.api_key is set (done in ocr_prompt).
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        base64_image = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
        ConfigParam = self.env['ir.config_parameter'].sudo()
        ai_model_id = ConfigParam.get_param('base_ai.ocr_model_id')
        if not ai_model_id:
            raise ValueError("No AI model configuration found. Please configure it in Settings.")

        ai_model = self.env['ai.model.config'].browse(int(ai_model_id))
        client = OpenAI(api_key=ai_model.api_key)
        # Hypothetical model
        response = client.chat.completions.create(model="gpt-4o-mini",  # Hypothetical model
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract the text from this image, ensuring all text is captured accurately. Do not include any markdown or code formatting."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ])
        return response.choices[0].message.content.strip()


def extract_json_from_response(response):
    """
    Extracts JSON content from the AI response.

    Args:
        response (str): The raw response from the AI.

    Returns:
        dict: The parsed JSON dictionary.

    Raises:
        ValueError: If JSON extraction or parsing fails.
    """
    # Define possible patterns
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
                continue  # Try the next pattern

    # If no valid JSON found
    raise ValueError("No valid JSON object found in the response.")