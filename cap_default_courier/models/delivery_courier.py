from odoo import models, fields

class DeliveryCourier(models.Model):
    _name = 'delivery.courier'
    _description = 'Delivery Courier'

    name = fields.Char(string="Name",required=True)
    type = fields.Selection([
            ('ltl','LTL'),
            ('courier','Courier'),
        ],
        string="Default Type",
        required=True)



