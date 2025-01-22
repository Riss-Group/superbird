from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    vin_number = fields.Char(compute='_compute_vin_number', string="Vin Number")
    stock_number = fields.Char(compute='_compute_stock_number', string="Stock Number")
    body_number = fields.Char(compute='_compute_body_number', string="Body Number")

    def _compute_vin_number(self):
        for line in self:
            concatenated_values = [vehicle.vin_sn or '' for vehicle in line.fleet_vehicle_ids]
            if len(concatenated_values) > 0:
                line.vin_number = ','.join(concatenated_values)
            else:
                line.vin_number = ''

    def _compute_stock_number(self):
        for line in self:
            concatenated_values = [vehicle.stock_number or '' for vehicle in line.fleet_vehicle_ids]
            if len(concatenated_values) > 0:
                line.stock_number = ','.join(concatenated_values)
            else:
                line.stock_number = ''

    def _compute_body_number(self):
        for line in self:
            concatenated_values = [vehicle.body_number or '' for vehicle in line.fleet_vehicle_ids]
            if len(concatenated_values) > 0:
                line.body_number = ','.join(concatenated_values)
            else:
                line.body_number = ''
