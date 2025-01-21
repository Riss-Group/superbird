# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_tax_applicable = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Tax Applicable", company_dependent=True)

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
        for rec in self.filtered(lambda r: not r.parent_id):
            if rec.is_tax_applicable == 'yes' and self.env.company.country_id.code == 'CA':
                if not rec.l10n_ca_pst or not rec.vat:
                    raise ValidationError(
                        "GST/HST Number and PST Number are required for Canadian companies when Tax Applicable is set to Yes.")
            if rec.is_tax_applicable == 'yes' and self.env.company.country_id.code == 'US' and not rec.vat:
                raise ValidationError("Tax ID is required for US companies when Tax Applicable is set to Yes.")

    @api.constrains('is_tax_applicable')
    def _change_tax_applicable(self):
        if self.env.company.country_id.code == 'CA':
            for rec in self:
                if not rec.is_tax_applicable == 'yes':
                    exemption_fiscal_position_id = self.env.company.sudo().tax_exemption_fiscal_position_id
                    if exemption_fiscal_position_id:
                        rec.property_account_position_id = exemption_fiscal_position_id
                else:
                    rec.property_account_position_id = False

    @api.model
    def _commercial_fields(self):
        res = super(ResPartner, self)._commercial_fields()
        res.append('is_tax_applicable')
        res.append('l10n_ca_pst')
        return res
