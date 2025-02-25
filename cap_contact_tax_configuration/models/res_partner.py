# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_tax_applicable = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Tax Applicable",
                                         company_dependent=True)
    tax_exempt_reason = fields.Many2one('tax.exempt.reason', string='Tax Exempt Reason', company_dependent=True)
    tax_exemption_certificate = fields.Binary('Exemption Certificate', help="Upload the exemption certificate.",
                                              company_dependent=True)
    certificate_name = fields.Char('Certificate Name', company_dependent=True)
    exemption_expiration_date = fields.Date('Exemption Expiration Date', help="Date when the exemption expires.",
                                            company_dependent=True)
    exemption_certificate_number = fields.Char('Certificate Number', help="Enter the certificate number.",
                                               company_dependent=True)

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
            if rec.is_tax_applicable == 'no' and self.env.company.country_id.code in ['CA', 'US']:
                if not rec.tax_exempt_reason:
                    raise ValidationError("Tax Exemption Reason is required!")
                if not rec.tax_exemption_certificate:
                    raise ValidationError("Tax Exemption Certificate is required!")
                if not rec.exemption_expiration_date:
                    raise ValidationError("Tax Exemption Expiration Date is required!")
                if not rec.exemption_certificate_number:
                    raise ValidationError("Tax Exemption Certificate Number is required!")

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
        res.append('tax_exemption_certificate')
        res.append('expiration_date')
        res.append('certificate_number')
        return res

    @api.model
    def _cron_send_expiration_email(self):
        company_ids = self.env['res.company'].sudo().search([])
        today = fields.Date.today()
        target_date = today + relativedelta(days=10)
        for company_id in company_ids:
            expiring_certificates = self.with_company(company_id).search([('exemption_expiration_date', '=', target_date)])
            template = self.env.ref(
                'cap_contact_tax_configuration.email_template_exemption_certificate_expiration_notification',
                raise_if_not_found=False)
            if not template:
                return True
            for certificate in expiring_certificates:
                notify_user_ids = company_id.mapped('exemption_notification_user_ids')
                if notify_user_ids:
                    recipient_emails = notify_user_ids.mapped('email')
                    if recipient_emails:
                        template.send_mail(
                            certificate.id,
                            force_send=True,
                            email_values={'email_to': ','.join(recipient_emails)}
                        )
        return True