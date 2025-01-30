# Copyright 2017 LasLabs Inc.
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MultiCompanyAbstract(models.AbstractModel):
    _inherit = "multi.company.abstract"

    @api.constrains("company_ids")
    def _check_add_branches(self):
        for record in self.sudo():
            if record.company_ids.mapped('child_ids'):
                all_companies_with_childs = record.company_ids | record.company_ids.mapped('child_ids')
                record.write(
                    {'company_ids': [(4, c) for c in all_companies_with_childs.ids]})
