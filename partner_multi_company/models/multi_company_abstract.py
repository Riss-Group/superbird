
from odoo import api, fields, models


class MultiCompanyAbstract(models.AbstractModel):
    _inherit = "multi.company.abstract"

    company_ids = fields.Many2many(
        'res.company',
        'res_partner_res_company_rel',
        'partner_id',
        'company_id',
        string='Companies'
    )
