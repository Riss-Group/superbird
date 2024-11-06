# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductPublicCategory(models.Model):
    _name = 'product.public.category'
    _inherit = 'product.public.category'
    _inherit = ['product.public.category', 'mail.thread']

