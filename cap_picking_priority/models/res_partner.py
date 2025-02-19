# -*- coding: utf-8 -*-

from odoo import models, fields, api


class resPartner(models.Model):
    _inherit = 'res.partner'


    is_customer_pick_up = fields.Boolean("Customer Pick-Up")