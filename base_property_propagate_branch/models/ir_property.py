import psycopg2

from odoo import models, fields, api
from odoo.exceptions import AccessError

class IrProperty(models.Model):
    _inherit = 'ir.property'

    @api.model
    def _set_multi(self, name, model, values, default_value=None):
        old_value = self._get_multi(name, model, list(values.keys()))
        company = self.env.company
        excluded_companies = self.env.context.get('excluded_companies', self.env['res.company']) + company
        if company.autopropagate_properties:
            target_companies = (self.env['res.company'].search([('parent_id', '=', False)]) if company.autopropagate_properties_all else company.child_ids) - excluded_companies
            for branch in target_companies:
                old_branch_value = self.with_company(branch)._get_multi(name, model,  list(values.keys()))
                alternate_record = None
                if self.env[model]._fields[name].type == 'many2one':
                    comodel = self.env[model]._fields[name].comodel_name
                    try:
                        try:
                            record = self.env[comodel].sudo(False).with_context(allowed_company_ids=branch.ids).browse(list(values.values()))
                            record.check_access_rule('read')
                        except psycopg2.ProgrammingError:
                            ids = [x.id for x in values.values()]
                            record = self.env[comodel].sudo(False).with_context(allowed_company_ids=branch.ids).browse(ids)
                            record.check_access_rule('read')
                    except AccessError:
                        if company.autopropagate_properties_name_search:
                            alternate_record = (self.env[comodel]
                                                .sudo(False)
                                                .with_context(allowed_company_ids=branch.ids)
                                                .name_search(record.sudo().display_name, limit=1))
                            if alternate_record:
                                for k in values.keys():
                                    values[k] = alternate_record[0][0]
                            else:
                                continue
                        else:
                            continue
                if old_value == old_branch_value or (alternate_record and all(old_value[x].display_name == old_branch_value[x].display_name for x in old_value.keys())):
                    self.with_company(branch).with_context(excluded_companies=excluded_companies)._set_multi(name, model, values, default_value)
        super()._set_multi(name, model, values, default_value)