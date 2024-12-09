from odoo import api, fields, models


class PortalWizardUser(models.TransientModel):
    _inherit = 'portal.wizard.user'

    accounting_information = fields.Boolean("Accounting", store=True, compute='_compute_access_value')
    project_information = fields.Boolean("Project", store=True, compute='_compute_access_value')
    helpdesk_information = fields.Boolean("Helpdesk", store=True, compute='_compute_access_value')

    @api.depends('partner_id', 'partner_id.accounting_information', 'partner_id.project_information',
                 'partner_id.helpdesk_information')
    def _compute_access_value(self):
        for portal_wizard_user in self:
            portal_wizard_user.accounting_information = portal_wizard_user.partner_id.accounting_information
            portal_wizard_user.project_information = portal_wizard_user.partner_id.project_information
            portal_wizard_user.helpdesk_information = portal_wizard_user.partner_id.helpdesk_information

    def action_grant_access(self):
        res = super(PortalWizardUser, self).action_grant_access()
        self.partner_id.sudo().write({'accounting_information': self.accounting_information,
                               'project_information': self.project_information,
                               'helpdesk_information': self.helpdesk_information})
        return res

