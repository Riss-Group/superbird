# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_fleet_vehicle = fields.Boolean(related='product_id.create_fleet_vehicle', store=True)
    parent_id = fields.Many2one('sale.order.line', compute='_compute_parent_id', store=False)
    child_ids = fields.One2many('sale.order.line', 'parent_id')
    product_sub_qty = fields.Float(string='Option Quantity', digits='Product Unit of Measure', default=1.0)

    @api.depends('product_sub_qty', 'parent_id', 'parent_id.product_uom_qty')
    def _compute_product_uom_qty(self):
        super()._compute_product_uom_qty()
        for rec in self.filtered(lambda x: x.parent_id):
            rec.product_uom_qty = rec.product_sub_qty * rec.parent_id.product_uom_qty

    @api.depends('order_id', 'order_id.order_line', 'order_id.order_line.is_fleet_vehicle')
    def _compute_parent_id(self):
        for rec in self:
            bus_line = rec.order_id.order_line.filtered(lambda x: x.is_fleet_vehicle and x != rec)
            rec.parent_id = bus_line and bus_line[0] or False

    @api.constrains('order_id.order_line.is_fleet_vehicle')
    def _check_only_one_bus_line(self):
        for rec in self:
            other_bus_lines = rec.order_id.order_line.filtered(lambda x: x.is_fleet_vehicle and x != rec)
            if other_bus_lines:
                raise ValidationError(_("Only one bus configuration can be sold in a specific Sale Order"))
