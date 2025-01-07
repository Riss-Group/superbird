from odoo import fields, api, models, _

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    approval_id = fields.Many2one('approval.request', string="Approval")
    command = fields.Integer(string="ORM Command")
    update_vals = fields.Char(string="ORM Update Values")
