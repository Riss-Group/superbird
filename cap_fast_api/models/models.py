from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class BaseModel(models.AbstractModel):
    _inherit = 'base'


    external_id_to_create = fields.Char(string='External ID to Create', store=True, copy=False)


    @api.model_create_multi
    def create(self, vals_list):
        '''
            Override of base's base create method. If external_id_to_create is set then it should be automatically generated
        '''
        records = super().create(vals_list)
        if 'external_id_to_create' in self._fields and self._auto:
            for record in records.filtered(lambda x: x.external_id_to_create):
                module = record.external_id_to_create.split('.')[0]
                name = record.external_id_to_create.split('.', 1)[1]
                existing_record = self.env['ir.model.data'].search([('module', '=', module), ('name', '=', name)])
                if not existing_record:
                    self.env['ir.model.data'].create({
                        'module': module,
                        'model': record._name,
                        'name': name,
                        'res_id': record.id
                    })
        return records
    

class PurchaseBillUnion(models.Model):
    _inherit = 'purchase.bill.union'


    external_id_to_create = fields.Char(string='External ID to Create', store=False, copy=False)


class AccountRoot(models.Model):
    _inherit='account.root'


    external_id_to_create = fields.Char(string='External ID to Create', store=False, copy=False)