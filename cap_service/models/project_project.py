from odoo import  models, fields, api
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = 'project.project'
    

    is_repair_service = fields.Boolean(string="Repair Service")