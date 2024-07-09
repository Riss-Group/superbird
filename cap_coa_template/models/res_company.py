from odoo import  models, fields, api
from odoo.exceptions import UserError

class ResCompany(models.Model):
    _inherit = 'res.company'   

    
    def action_create_missing_coa(self):
        '''
            This method is intended to be used as a button action
            It will search the corp coa for child accounts and if they dont exist create them
        '''
        account_template_ids = self.env['account.account.template'].search([])
        for account_template_id in account_template_ids:
            account_id = self.env['account.account'].sudo().search([
                ('company_id', '=', self.id),
                ('name', '=', account_template_id.name ),
                ('code', '=', account_template_id.code ),
            ])
            if not account_id:
                vals = account_template_id.get_vals_dict(self.id)
                self.env['account.account'].sudo().create(vals)