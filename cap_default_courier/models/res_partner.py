# -*- coding: utf-8 -*-
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    default_courier_id = fields.Many2one("delivery.carrier", string="Default Courier")
    default_ltl_id = fields.Many2one("delivery.carrier", string="Default LTL")
