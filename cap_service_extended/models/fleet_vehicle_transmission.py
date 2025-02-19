# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FleetVehicleTransmission(models.Model):
    _name = 'fleet.vehicle.transmission'
    _description = 'Vehicle Transmission'

    manufacturer = fields.Char(string="Manufacturer", required=True)
    model = fields.Char(string="Model", required=True)
    transmission_type = fields.Selection(
        [('automatic', 'Automatic'), ('manual', 'Manual')],
        string="Transmission Type",
        default='manual'
    )
    speeds = fields.Integer(string="Number of Speeds")

    def _compute_display_name(self):
        for record in self:
            parts = [
                record.manufacturer,
                record.model,
                record.transmission_type,
                '{} speeds'.format(record.speeds) if record.speeds else '',
            ]
            record.display_name = ' '.join(filter(None, parts))
