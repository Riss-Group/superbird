# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _order = 'priority desc, scheduled_date asc, id desc'


    priority = fields.Selection([
        ('0', 'Very Low'),
        ('1', 'Low'),
        ('2', 'Normal'),
        ('3', 'High'),
        ('4', 'Very High')], string="Priority")

class StockMove(models.Model):
    _inherit = 'stock.move'


    priority = fields.Selection([
        ('0', 'Very Low'),
        ('1', 'Low'),
        ('2', 'Normal'),
        ('3', 'High'),
        ('4', 'Very High')], string="Priority", default="1")


