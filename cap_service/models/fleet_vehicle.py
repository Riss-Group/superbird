from odoo import  models, fields, api, _
from odoo.exceptions import UserError


class FleetVehicleWarrantyLine(models.Model):
    _inherit = 'fleet.vehicle'
    

    fleet_vehicle_warranty_line = fields.One2many('fleet.vehicle.warranty.line', 'fleet_vehicle_id')
    stock_number = fields.Char()