from odoo import http
from odoo.http import request

class NotificationController(http.Controller):
    @http.route('/notification/get_autoclose_delay', type='json', auth='user')
    def get_autoclose_delay(self):
        return request.env['ir.config_parameter'].sudo().get_param('notification.autoclose_delay', default=4000)
