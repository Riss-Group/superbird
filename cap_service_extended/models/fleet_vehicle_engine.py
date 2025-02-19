# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FleetVehicleEngine(models.Model):
    _name = 'fleet.vehicle.engine'
    _description = 'Vehicle Engine'

    manufacturer = fields.Char(string="Manufacturer", required=True)
    model = fields.Char(string="Model", required=True)
    size = fields.Char(string="Size")
    cylinders = fields.Integer(string="Cylinders")
    horsepower = fields.Integer(string="Horsepower")

    def _compute_display_name(self):
        for record in self:
            parts = [
                record.manufacturer,
                record.model,
                record.size,
                '{}cyl'.format(record.cylinders) if record.cylinders else '',
                '{}hp'.format(record.horsepower) if record.horsepower else '',
            ]
            record.display_name = ' '.join(filter(None, parts))
