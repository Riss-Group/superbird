from odoo import models, fields, api
from odoo.exceptions import AccessError

class IrProperty(models.Model):
    _inherit = 'ir.property'

    @api.model
    def _set_multi(self, name, model, values, default_value=None):
        old_value = self._get_multi(name, model, list(values.keys()))
        company = self.env.company
        if company.autopropagate_properties:
            for branch in company.child_ids:
                old_branch_value = self.with_company(branch)._get_multi(name, model,  list(values.keys()))
                if self.env[model]._fields[name].type == 'many2one':
                    comodel = self.env[model]._fields[name].comodel_name
                    try:
                        record = self.env[comodel].sudo(False).with_context(allowed_company_ids=branch.ids).browse(list(values.values()))
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
                if old_value == old_branch_value:
                    self.with_company(branch)._set_multi(name, model, values, default_value)
        super()._set_multi(name, model, values, default_value)