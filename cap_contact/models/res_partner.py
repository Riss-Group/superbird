from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'


    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []

        res_partner_search_mode = self.env.context.get('res_partner_search_mode')
        if res_partner_search_mode == 'customer':
            args = [('customer_rank', '=', True)] + args
        elif res_partner_search_mode == 'supplier':
            args = [('supplier_rank', '=', True)] + args

        return super().name_search(name,args,operator,limit)

    @api.model_create_multi
    def create(self, vals_list):
        partners = super(ResPartner, self).create(vals_list)
        for partner in partners:
            parent = partner.parent_id
            if parent:
                partner.is_customer = parent.is_customer
                partner.is_supplier = parent.is_supplier
        return partners


