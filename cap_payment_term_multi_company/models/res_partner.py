# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains('property_payment_term_id')
    def _compute_property_payment_term_id(self):
        for partner in self:
            if self.env.company.child_ids:
                for company in self.env.company.child_ids:
                    if company.id not in self.property_payment_term_id.company_ids.ids:
                        continue
                    property_id = self.env['ir.property'].sudo().search([('company_id', '=', company.id),
                                                                         ('res_id', '=', 'res.partner,%s' % partner.id),
                                                                         ('name', '=', 'property_payment_term_id')], limit=1)
                    if not property_id:
                        property_vals = partner.prepare_property_vals(partner.property_payment_term_id,
                                                                      self.env['ir.model.fields']._get('res.partner', 'property_payment_term_id'),
                                                                      company)
                        self.env['ir.property'].sudo().create(property_vals)
                    elif property_id:
                        property_id.sudo().write({'value_reference': 'account.payment.term,%s' % partner.property_payment_term_id.id})

    @api.constrains('property_supplier_payment_term_id')
    def _compute_property_supplier_payment_term_id(self):
        for partner in self:
            if self.env.company.child_ids:
                for company in self.env.company.child_ids:
                    if company.id not in self.property_supplier_payment_term_id.company_ids.ids:
                        continue
                    property_id = self.env['ir.property'].sudo().search([('company_id', '=', company.id),
                                                                         ('res_id', '=', 'res.partner,%s' % partner.id),
                                                                         ('name', '=', 'property_supplier_payment_term_id')], limit=1)
                    if not property_id:
                        property_vals = partner.prepare_property_vals(partner.property_supplier_payment_term_id,
                                                                   self.env['ir.model.fields']._get('res.partner', 'property_supplier_payment_term_id'),
                                                                   company)
                        self.env['ir.property'].sudo().create(property_vals)
                    elif property_id:
                        property_id.sudo().write({'value_reference': 'account.payment.term,%s' % partner.property_supplier_payment_term_id.id})

    def prepare_property_vals(self, payment_term_id, fields_id, company_id):
        return  {'fields_id': fields_id.id,
                 'company_id': company_id.id,
                 'res_id': 'res.partner,%s' % self.id,
                 'name': fields_id.name,
                 'value_reference': 'account.payment.term,%s' % payment_term_id.id,
                 'type': 'many2one'}
