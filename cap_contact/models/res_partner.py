from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = 'res.partner'



    @api.model
    def _name_search(self, name, domain=None, operator="ilike", limit=None, order=None):
        res_partner_search_mode = self.env.context.get('res_partner_search_mode')
        if not domain:
            return super()._name_search(name, domain, operator, limit, order)
        if res_partner_search_mode == 'customer':
            domain = ['|', ('customer_rank', '=', True)] + domain
        elif res_partner_search_mode == 'supplier':
            domain = ['|', ('supplier_rank', '=', True)] + domain
        return super()._name_search(name, domain, operator, limit, order)

    @api.model_create_multi
    def create(self, vals_list):
        partners = super(ResPartner, self).create(vals_list)
        for partner in partners:
            parent = partner.parent_id
            if parent:
                partner.is_customer = parent.is_customer
                partner.is_supplier = parent.is_supplier
        return partners


