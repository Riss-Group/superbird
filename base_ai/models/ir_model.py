from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval
import json

class IrModel(models.Model):
    _inherit = 'ir.model'

    ocr_enabled = fields.Boolean(string="OCR Enabled", help="Enable or disable OCR for this model.")
    extra_instructions_ocr = fields.Text(
        string="Extra Instructions for OCR",
        help="Extra instructions appended to OCR prompts."
    )
    extra_instructions_ai = fields.Text(
        string="Extra Instructions for AI",
        help="Extra instructions appended to AI prompts."
    )
    ai_query_enabled = fields.Boolean(string="AI Query Enabled", help="Enable or disable AI queries for this model.")
    ai_exposed_field_ids = fields.Many2many(
        comodel_name='ir.model.fields',
        relation='model_ai_exposed_field_rel',
        column1='model_id',
        column2='field_id',
        string='Exposed Fields',
        domain="[('model_id', '=', id)]",
        help="Select which fields are exposed."
    )
    ai_obfuscated_field_ids = fields.Many2many(
        comodel_name='ir.model.fields',
        relation='model_ai_obfuscated_field_rel',
        column1='model_id',
        column2='field_id',
        string='Obfuscated Fields',
        domain="[('model_id', '=', id)]",
        help="Select which fields are obfuscated."
    )

    ai_exposed_domain = fields.Char(
        string='AI Exposed Domain',
        help='Domain to filter records when building possible_values. E.g. "[(\'active\', \'=\', True)]"'
    )

    max_tokens = fields.Integer(
        string='Max Tokens (Override)',
        help="Override the max tokens defined in the AI model configuration. If empty or zero, uses the AI model's setting."
    )
    temperature = fields.Float(
        string='Temperature (Override)',
        help="Override the temperature defined in the AI model configuration. If empty, uses the AI model's setting."
    )

    max_depth = fields.Integer(
        string='Maximum recursion depth',
        help="Set the maximum recursion depth when fetching data from relational fields of this model.",
        default=2
    )

    def get_json_structure(self):
        self.ensure_one()
        data = {
            'model': self.model,
            'fields': self._build_field_structure(self.ai_exposed_field_ids)
        }
        return json.dumps(data, indent=2)

    def _build_field_structure(self, field_records, depth=0):
        self.ensure_one()
        max_depth = self.max_depth or 2
        if depth > max_depth:
            return {}

        fields_data = {}
        env = self.env
        ir_model_obj = env['ir.model']

        for field_rec in field_records.filtered(lambda x: not x.readonly):
            field_info = {
                'type': field_rec.ttype,
                'description': field_rec.field_description,
                'required': field_rec.required,
            }

            related_model_name = field_rec.relation
            if related_model_name:
                related_model = ir_model_obj.search([('model', '=', related_model_name)], limit=1)
                if related_model:
                    if field_rec.ttype in ('many2one', 'many2many'):
                        # For many2one and many2many, use _get_possible_values
                        related_fields = related_model.ai_exposed_field_ids
                        possible_values = self._get_possible_values(
                            related_model_name, related_fields, related_model, depth=depth+1
                        )
                        field_info['possible_values'] = possible_values
                    elif field_rec.ttype == 'one2many':
                        # For one2many, recursively build field structure
                        related_exposed_fields = related_model.ai_exposed_field_ids
                        nested_fields = self._build_field_structure(
                            related_exposed_fields, depth=depth+1
                        )
                        field_info['exposed_fields'] = nested_fields

            fields_data[field_rec.name] = field_info

        return fields_data

    def _get_possible_values(self, model_name, field_records, related_model_record, depth=0):
        env = self.env
        model_obj = env[model_name]

        domain_str = related_model_record.ai_exposed_domain or '[]'
        try:
            domain = safe_eval(domain_str)
        except Exception:
            domain = []

        all_records = model_obj.search(domain)
        fields_data = self._build_field_structure(field_records, depth=depth)

        values = []
        for rec in all_records:
            rec_data = {'id': rec.id, 'display_name': rec.display_name}
            for field_name, field_info in fields_data.items():
                val = rec[field_name]
                if field_info['type'] == 'many2one':
                    rec_data[field_name] = val.id if val else False
                elif field_info['type'] == 'many2many':
                    rec_data[field_name] = val.ids
                else:
                    rec_data[field_name] = val
            values.append(rec_data)

        return values
