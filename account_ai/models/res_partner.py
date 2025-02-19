from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    extra_instructions = fields.Text(string="Extra Instructions")
    ocr_template_move_id = fields.Many2one(
        'account.move',
        string='Bill Template',
        domain="[('partner_id', '=', id), ('move_type', '=', 'in_invoice')]"
    )