# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SalesRestriction(models.Model):
    _name = 'sale.restriction'
    _description = 'Sales Restriction'

    name = fields.Char(required=True)
    customer_domain = fields.Char()
    allowed_products = fields.Char()


