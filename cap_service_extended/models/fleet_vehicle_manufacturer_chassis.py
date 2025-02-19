# -*- coding: utf-8 -*-
from odoo import models, fields

class FleetVehicleManufacturerChassis(models.Model):
    _name = 'fleet.vehicle.manufacturer.chassis'
    _description = 'Chassis Manufacturer'

    name = fields.Char(string="Chassis Manufacturer Name", required=True)
