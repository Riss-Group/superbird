# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FleetVehicleModel(models.Model):
    _inherit = 'fleet.vehicle.model'

    chassis_manufacturer_id = fields.Many2one(
        'fleet.vehicle.manufacturer.chassis',
        string="Chassis Manufacturer"
    )

    def _compute_display_name(self):
        for record in self:
            manufacturer = record.brand_id.name if record.brand_id else ''
            chassis = record.chassis_manufacturer_id.name if record.chassis_manufacturer_id else ''
            model_name = record.name or ''
            record.display_name = " / ".join(filter(None, [manufacturer, chassis, model_name]))