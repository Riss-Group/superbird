from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ocr_model_id = fields.Many2one(
        'ai.model',
        string='Model to use for OCR',
        config_parameter='base_ai.ocr_model_id'
    )

    ocr_service = fields.Selection([
        ('pytesseract', 'Local OCR (pytesseract)'),
        ('google_vision', 'Google Vision'),
        ('aws_textract', 'AWS Textract'),
        ('openai_vision', 'OpenAI Vision'),
    ], string='OCR Service', default='pytesseract', config_parameter='base_ai.ocr_service')

    google_vision_api_key = fields.Char(
        string='Google Vision API Key',
        config_parameter='base_ai.google_vision_api_key',
        help="API Key for Google Vision. Actual usage often requires service accounts."
    )

    aws_access_key_id = fields.Char(
        string='AWS Access Key ID',
        config_parameter='base_ai.aws_access_key_id'

    )
    aws_secret_access_key = fields.Char(
        string='AWS Secret Access Key',
        config_parameter='base_ai.aws_secret_access_key'
    )
    aws_region = fields.Char(
        string='AWS Region',
        config_parameter='base_ai.aws_region',
        default='us-east-1',
        help="AWS Region for Textract (e.g. us-east-1)."
    )

    query_model_id = fields.Many2one(
        'ai.model',
        string='Model to use for AI Query',
        config_parameter='base_ai.query_model_id'
    )
