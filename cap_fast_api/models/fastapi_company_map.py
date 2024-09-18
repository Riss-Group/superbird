from odoo import models, fields, api


class FastApiCompanyMap(models.Model):
    _name = "fastapi.company.map"
    _description = "FastAPI Company Map"


    name = fields.Char()
    company_id = fields.Many2one('res.company')