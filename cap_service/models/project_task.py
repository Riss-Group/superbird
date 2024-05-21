from odoo import  models, fields, api
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'
    

    name = fields.Char(string='Description')
    cause = fields.Char()
    correction = fields.Char()