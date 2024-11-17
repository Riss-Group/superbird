from odoo import  models, fields, api, _


class FleetVehicleModel(models.Model):
    _inherit = 'fleet.vehicle.model'
    

    is_bus_fleet = fields.Boolean(related='brand_id.is_bus_fleet')