from odoo import fields, models


class ExceptionRuleGroup(models.Model):
    _name = "exception.rule.group"


    name = fields.Char('Name')
