from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'


    statement_display_name = fields.Char()