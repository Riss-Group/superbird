# -*- coding: utf-8 -*-
from odoo import fields, models, api


class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'
    
    cost_subtotal = fields.Float(required=True, digits='Account', default=0, compute='get_cost_subtotal', string='Total DT')
    cost_unit = fields.Float(required=True, digits='Account', default=0, string='DT unitaire')
    price_base = fields.Float(required=True, digits='Account', default=0, string='Prix de base')

    @api.depends('cost_unit', 'product_qty')
    def get_cost_subtotal(self):
        for line in self:
            line.cost_subtotal = line.cost_unit * line.product_qty

    @api.onchange('cost_unit')
    def onchane_cost_unit(self):
        for line in self:
            line.price_unit = line.price_base + line.cost_unit
    
    @api.onchange('price_unit')
    def onchane_price_unit(self):
        for line in self:
            line.price_base = line.price_unit - line.cost_unit

    @api.onchange('price_base')
    def onchane_price_base(self):
        for line in self:
            line.price_unit = line.cost_unit + line.price_base


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    delivery_cost = fields.Float(digits='Account', compute='get_delivery_cost', string='Total DT')
    
    @api.depends('order_line')
    def get_delivery_cost(self):
        cost = 0
        for line in self.order_line:
            cost += line.cost_subtotal
        self.delivery_cost = cost
