from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'
    

    service_order_id = fields.Many2one('service.order')
    service_order_type = fields.Selection([
        ('Customer','Customer'),
        ('Warranty','Warranty'),
        ('Internal','Internal'),
    ])
    