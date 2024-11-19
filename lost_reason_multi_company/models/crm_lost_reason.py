# Copyright 2015 Oihane Crucelaegui
# Copyright 2015-2019 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html.html

from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError


class CrmLostReaon(models.Model):
    _inherit = ["multi.company.abstract", "crm.lost.reason"]
    _name = "crm.lost.reason"


    company_ids = fields.Many2many(
        "res.company",
        relation="crm_lost_reason_company_rel",  # Unique relation table name
        string="Companies",
    )