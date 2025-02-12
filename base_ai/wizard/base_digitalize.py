from odoo import models, fields, api
import base64

from odoo.exceptions import UserError


class BaseDigitalize(models.TransientModel):
    _name = 'base.digitalize'
    _description = 'Wizard to upload a file for OCR and update the current record'

    file = fields.Binary(string="File", required=False)
    filename = fields.Char(string="Filename")
    res_model = fields.Char(default=lambda self: self._context.get('active_model'))
    res_id = fields.Integer(default=lambda self: self._context.get('active_id'))
    attachment_ids = fields.Many2many('ir.attachment', string="Possible attachments", store=False, compute='_compute_attachment_ids')
    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Existing attachment',
        domain="[('id', 'in', attachment_ids)]",
        compute='_compute_attachment_id',
        readonly=False
    )

    @api.depends('res_model', 'res_id')
    def _compute_attachment_ids(self):
        for rec in self:
            record = self.env[rec.res_model].browse(rec.res_id)
            if hasattr(record, 'attachment_ids'):
                rec.attachment_ids = record.attachment_ids
            else:
                rec.attachment_ids = False

    @api.depends('res_model', 'res_id')
    def _compute_attachment_id(self):
        for rec in self:
            record = self.env[rec.res_model].browse(rec.res_id)
            if hasattr(record, 'message_main_attachment_id'):
                rec.attachment_id = record.message_main_attachment_id
            else:
                rec.attachment_ids = False

    def action_load_attachment(self):
        self.ensure_one()
        if self.attachment_id:
            self.file = self.attachment_id.datas
            self.filename = self.attachment_id.name
            return {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }

    def action_confirm(self):
        self.ensure_one()
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if not active_model or not active_id:
            return

        record = self.env[active_model].browse(active_id)
        force_company = record.company_id if hasattr(record, 'company_id') else False
        data = record.with_context(
            file_name=self.filename,
            force_company=record.company_id if hasattr(record, 'company_id') else False
        ).ocr_prompt(base64.b64decode(self.file))
        if hasattr(record, 'attachment_ids') and self.file not in record.attachment_ids.mapped('datas'):
            self.env['ir.attachment'].create({
                'name': self.filename,
                'datas': self.file,
                'res_model': self.res_model,
                'res_id': self.res_id,
            })
        fields_data = data.get('fields', {})
        vals = self.convert_commands(record, fields_data)

        if vals:
            try:
                record.write(vals)
            except Exception as e:
                raise UserError("exception: %s\n vals: %s" % (e, vals))

        return {'type': 'ir.actions.act_window_close'}

    def convert_commands(self, model, fields_data):
        """
        Recursively converts lists of dicts into lists of command tuples for relational fields.

        Args:
            model (models.Model): The Odoo model instance.
            fields_data (dict): The dictionary containing field data.

        Returns:
            dict: A dictionary with converted command tuples.
        """
        commands = {}
        model_fields = model.fields_get()

        for field_name, value in fields_data.items():
            if field_name in model_fields:
                field_type = model_fields[field_name]['type']

                if field_type in ('one2many', 'many2many'):
                    if isinstance(value, list):
                        if field_type == 'one2many':
                            # For one2many, recursively convert nested fields
                            nested_model = model_fields[field_name]['relation']
                            nested_records = []
                            for line in value:
                                nested_vals = self.convert_commands(self.env[nested_model].browse(), line)
                                nested_records.append(fields.Command.create(nested_vals))
                            commands[field_name] = nested_records
                        else:
                            commands[field_name] = [fields.Command.link(line) for line in value]
                else:
                    commands[field_name] = value

        return commands