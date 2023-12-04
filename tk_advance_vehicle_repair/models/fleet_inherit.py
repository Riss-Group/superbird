# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class FleetVehicle(models.Model):
    """Fleet Vehicle"""
    _inherit = 'fleet.vehicle'
    _description = __doc__

    vehicle_brand_id = fields.Many2one('vehicle.brand', string="Vehicle Name")
    vehicle_model_id = fields.Many2one('vehicle.model', string=" Model",
                                       domain="[('vehicle_brand_id', '=', vehicle_brand_id)]")
    vehicle_fuel_type_id = fields.Many2one('vehicle.fuel.type', string=" Fuel Type")
    transmission_type = fields.Selection([('manual', "Manual"), ('automatic', "Automatic"), ('cvt', "CVT")],
                                         string="Transmission Type")
    vin_no = fields.Char(string="VIN Number")
