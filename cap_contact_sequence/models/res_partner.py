# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    id_number = fields.Integer(string="ID Number")
    historical_id_number = fields.Integer(string="Legacy Number")
    sequence = fields.Integer()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence', '') == '':
                # company_id = vals.get('company_id', self.env.company.id)
                # vals['sequence'] = self.env['ir.sequence'].with_company(company_id).next_by_code('picking.batch') or '/'
                vals['sequence'] = self.env['ir.sequence'].next_by_code('res.partner.sequence') or ''
            if vals.get('id_number', '') == '':
                vals['id_number'] = self.env['ir.sequence'].next_by_code('res.partner.id_number') or ''
        return super().create(vals_list)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        try :
            id_number = int(name)
        except :
            id_number = False
        if id_number:
            args +=  ['|','|', ('id_number', 'like', id_number), ('historical_id_number', 'like', id_number)]
        return super().name_search(name,args,operator,limit)

