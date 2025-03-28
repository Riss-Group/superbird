import psycopg2

from odoo import models, fields, api
from odoo.exceptions import AccessError

class IrProperty(models.Model):
    _inherit = 'ir.property'

    @api.model
    def _set_multi(self, name, model, values, default_value=None):

        def clean(value):
            return value.id if isinstance(value, models.BaseModel) else value

        old_value = self._get_multi(name, model, list(values.keys()))
        company = self.env.company
        excluded_companies = self.env.context.get('excluded_companies', self.env['res.company']) + company
        if company.autopropagate_properties:
            target_companies = (self.env['res.company'].search([('parent_id', '=', False)]) if company.autopropagate_properties_all else company.child_ids) - excluded_companies
            for branch in target_companies:
                branch_values = values.copy()
                old_branch_value = self.with_company(branch)._get_multi(name, model,  list(branch_values.keys()))
                alternate_record = None
                if self.env[model]._fields[name].type == 'many2one':
                    comodel = self.env[model]._fields[name].comodel_name
                    try:
                        # try:
                        record = self.env[comodel].sudo(False).with_context(allowed_company_ids=branch.ids).browse([clean(x) for x in branch_values.values() if x])
                        if not record or isinstance(record, AccessError):
                            raise AccessError('')
                        record = record[0]
                        record.check_access_rights("write")
                        record.check_access_rule("write")
                        # except psycopg2.ProgrammingError:
                        #     ids = [x.id for x in values.values()]
                        #     record = self.env[comodel].sudo(False).with_context(allowed_company_ids=branch.ids).browse(ids)
                        #     record.check_access_rule('read')
                    except AccessError:
                        if company.autopropagate_properties_name_search:
                            alternate_record = (self.env[comodel]
                                                .sudo(False)
                                                .with_context(allowed_company_ids=branch.ids)
                                                .name_search(record.sudo().display_name, limit=1))
                            if alternate_record:
                                for k in branch_values.keys():
                                    branch_values[k] = alternate_record[0][0]
                            else:
                                continue
                        else:
                            continue
                if (
                    self.env.context.get('force_propagate', False) or
                    old_value == old_branch_value or
                    (alternate_record and all(old_value[x].display_name == old_branch_value[x].display_name for x in old_value.keys()))
                ):
                    self.with_company(branch).with_context(excluded_companies=excluded_companies)._set_multi(name, model, branch_values, default_value)
        super()._set_multi(name, model, values, default_value)