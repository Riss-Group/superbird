
from odoo import fields, models


class CrmStage(models.Model):
    _inherit = "crm.stage"


    company_id = fields.Many2one(
        "res.company", related="team_id.company_id")