from odoo import fields, models


class ExceptionRule(models.Model):
    _inherit = "exception.rule"

    exception_group = fields.Many2one("exception.rule.group", string="Group")