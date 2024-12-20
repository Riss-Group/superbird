from odoo import  models, fields, api
from odoo.exceptions import UserError


class ServiceLineViewProduct(models.TransientModel):
    _name = 'service.ccc.edit'   
    _description = 'Service CCC Edit'


    service_line_id = fields.Many2one('service.order.line')
    name = fields.Text(related="service_line_id.name", store=True, readonly=False)
    cause = fields.Text(related="service_line_id.cause", store=True, readonly=False)
    correction = fields.Text(related="service_line_id.correction", store=True, readonly=False)


    def button_save (self):
        return True
