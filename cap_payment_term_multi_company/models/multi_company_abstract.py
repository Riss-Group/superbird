from odoo import api, fields, models


class MultiCompanyAbstract(models.AbstractModel):
    _inherit = "multi.company.abstract"

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        new_domain = self._patch_company_domain(domain)
        return super()._search(new_domain, offset, limit, order, access_rights_uid)
