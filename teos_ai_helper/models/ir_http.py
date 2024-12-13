from odoo import models


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        """
        Inherit function to added info if the user belongs to ai search group or not
        :return:
        """
        user = self.env.user
        session_info = super().session_info()
        session_info['is_ai_user'] = user.has_group('teos_ai_helper.group_ai_user')
        return session_info
