from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    ai_prompt = fields.Text(default="""You are a Postgres expert and Odoo expert.
    Given the table names, Definitions and a prompt.
    You only return sql queries that we can run directly no natural language.
    Strictly stick to columns and table names provided in the table definition.
    The question is:""")
    ai_model_ids = fields.Many2many('ir.model')
