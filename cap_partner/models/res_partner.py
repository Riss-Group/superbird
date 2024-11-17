from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    type = fields.Selection(selection_add=[('support_contact', 'Support Contact')])
