from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    accounting_information = fields.Boolean("Accounting", default=True)
    project_information = fields.Boolean("Project", default=True)
    helpdesk_information = fields.Boolean("Helpdesk", default=True)
    is_portal_user = fields.Boolean(string="Is Portal User", compute='_compute_is_portal_user', store=True,
                                    compute_sudo=True, default=False)

    @api.depends('user_ids', 'user_ids.share')
    def _compute_is_portal_user(self):
        for record in self:
            record.is_portal_user = record.user_ids.filtered(lambda u: u.share)