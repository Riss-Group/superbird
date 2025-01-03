from odoo import  models, fields, api
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = 'project.project'
    

    is_repair_service = fields.Boolean(string="Repair Service")


    @api.depends('is_fsm', 'is_repair_service')
    def _compute_allow_quotations(self):
        super()._compute_allow_quotations()
        for record in self:
            record.allow_quotations = record.is_repair_service