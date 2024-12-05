# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_tax_applicable = fields.Boolean(string="Tax Applicable", company_dependent=True)

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        res.check_tax_fields()
        return res

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        self.check_tax_fields()
        return res

    def check_tax_fields(self):
        for rec in self:
            if rec.is_tax_applicable and self.env.company.country_id.code == 'CA':
                if not rec.l10n_ca_pst or not rec.vat:
                    raise ValidationError(
                        "GST/HST Number and PST Number are required for Canadian companies when Tax Applicable is set to Yes.")
            if rec.is_tax_applicable and self.env.company.country_id.code == 'US' and not rec.vat:
                raise ValidationError("Tax ID is required for US companies when Tax Applicable is set to Yes.")

    @api.constrains('is_tax_applicable')
    def _change_tax_applicable(self):
        for rec in self:
            if rec.is_tax_applicable:
                exemption_fiscal_position_id = self.env.company.sudo().tax_exemption_fiscal_position_id
                if exemption_fiscal_position_id:
                    rec.property_account_position_id = exemption_fiscal_position_id
            else:
                rec.property_account_position_id = False
