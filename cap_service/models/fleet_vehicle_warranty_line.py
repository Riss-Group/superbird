from odoo import  models, fields, api, _
from odoo.exceptions import UserError


class FleetVehicleWarrantyLine(models.Model):
    _name = 'fleet.vehicle.warranty.line'
    _description = 'Fleet Vehicle Warranty Line'


    fleet_vehicle_id = fields.Many2one('fleet.vehicle')
    warranty_description = fields.Char()
    mileage_expiration = fields.Integer()
    date_expiration = fields.Date()

