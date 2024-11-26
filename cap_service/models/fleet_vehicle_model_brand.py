from odoo import  models, fields, api, _


class FleetVehicleModelBrand(models.Model):
    _inherit = 'fleet.vehicle.model.brand'
    

    is_bus_fleet = fields.Boolean()