from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime 
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self, vals):

        fields_list = [
            'bank_ids',
            'acc_number',
            'allow_payment',
            'acc_holder_name',
            'credit',
            'days_sales_outstanding',
            'use_partner_credit_limit',
            'credit_limit',
        ]
        field_keys = set(fields_list)
        val_keys = set(vals.keys())

        if field_keys & val_keys:
            category_id = self.env['approval.category'].search([('name','=','Change Contact Accounting Info')],limit=1).id
            for partner in self:
                partner_id = self.env['res.partner'].search([('id','=',partner.id)]).id
                approval_data = {
                    'date': fields.Datetime.now(),
                    'partner_id': partner_id,
                    'category_id': category_id,
                }
                # raise UserError(f"{partner_id}\n\n{self.id}")
                for field in field_keys:
                    if field in vals:  
                        if field == 'bank_ids':
                            bank_ids_dict = vals.get('bank_ids', {})
                            for subfield, value in bank_ids_dict.items():
                                print(f"Processing {subfield}: {value}")
                                approval_data[subfield] = value
                        else:
                            field_data = vals.get(field)
                            print(f"Processing {field}: {field_data}")
                            approval_data[field] = field_data
                _logger.info(f"\n\n{approval_data}\n\n") 
                approval = self.env['approval.request'].create(approval_data)
                self.env.cr.commit()
                raise UserError(f"Approval, {approval.name}, has been created and the approval process to make the changes to Bank Accounts and/or Credit Limits has begun")
            
        return super().write(vals)
