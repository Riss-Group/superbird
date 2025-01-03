# -*- coding: utf-8 -*-
from odoo import models, fields

class AiMessage(models.Model):
    _name = 'ai.message'
    _description = 'AI Chat Message'
    _order = 'id asc'

    res_id = fields.Integer(string='Resource ID', index=True)
    res_model = fields.Char(string='Resource Model', index=True)
    role = fields.Selection([
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ], string='Role', required=True)
    content = fields.Text(string='Content', required=True)
