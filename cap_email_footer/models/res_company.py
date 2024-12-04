from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    custom_email_ids = fields.One2many("custom.email","company_id",string="Custom Emails")
    

