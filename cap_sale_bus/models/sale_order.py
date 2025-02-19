from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    bus_line_id = fields.Many2one('sale.order.line', compute='_compute_bus_line_id')
    vehicle_year = fields.Selection(related='bus_line_id.product_id.vehicle_year')
    vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand', related='bus_line_id.product_id.vehicle_make_id')
    vehicle_model_id = fields.Many2one('fleet.vehicle.model', related='bus_line_id.product_id.vehicle_model_id')

    @api.depends('order_line', 'order_line.is_fleet_vehicle')
    def _compute_bus_line_id(self):
        for rec in self:
            rec.bus_line_id = rec.order_line.filtered(lambda x: x.is_fleet_vehicle) and rec.order_line.filtered(lambda x: x.is_fleet_vehicle)[0] or False