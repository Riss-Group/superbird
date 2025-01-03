# -*- coding: utf-8 -*-
from odoo import models, fields

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    type = fields.Selection([('ltl','LTL'), ('courier','Courier')], string="Default Type", default='courier')



