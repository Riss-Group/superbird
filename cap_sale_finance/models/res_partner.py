from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    financing_partner = fields.Boolean("Financing Partner")
