from odoo import models, fields, api

class CustomEmail(models.Model):
    _name = 'custom.email'
    _description = 'Custom Emails'

    email = fields.Char(string="Email")
    report_action_ids = fields.Many2many("ir.actions.report",string="Report Actions")
    company_id = fields.Many2one("res.company",string="Company")


