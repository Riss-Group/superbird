from odoo import models, fields, api, _
from odoo.exceptions import AccessError


class Project(models.Model):
    _inherit = 'project.project'

    def action_project_sharing_view_so(self):
        """
        checks for portal user
        """
        if self.env.user.has_group('base.group_user') or (
                self.env.user.has_group('base.group_portal') and self.env.user.partner_id.accounting_information):
            return super().action_project_sharing_view_so()
        else:
            raise AccessError(_('You are not authorized to access the sale order.'))