from odoo import models, fields, api


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'


    service_line_id = fields.Many2one('service.order.line')