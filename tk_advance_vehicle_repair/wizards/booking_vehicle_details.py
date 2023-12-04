# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models, _


class BookingVehicleDetails(models.TransientModel):
    """Booking Vehicle Details"""
    _name = 'booking.vehicle.details'
    _description = __doc__

    vehicle_booking_id = fields.Many2one('vehicle.booking', string="Vehicle Booking")
    vehicle_type = fields.Selection([('fleet_vehicle', "Vehicle From Fleet"),
                                     ('customer_vehicle', "Vehicle From Customer")], string="Vehicle Type")
    customer_id = fields.Many2one('res.partner')
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Fleet Vehicle")
    register_vehicle_id = fields.Many2one('register.vehicle', string="Customer Vehicle",
                                          domain="[('customer_id','=',customer_id)]")
    vehicle_brand_id = fields.Many2one('vehicle.brand', string="Vehicle")
    vehicle_model_id = fields.Many2one('vehicle.model', string="Model",
                                       domain="[('vehicle_brand_id', '=', vehicle_brand_id)]")
    registration_no = fields.Char(string="Registration No", translate=True)
    vehicle_fuel_type_id = fields.Many2one('vehicle.fuel.type', string="Fuel Type")
    transmission_type = fields.Selection([('manual', "Manual"), ('automatic', "Automatic"), ('cvt', "CVT")],
                                         string="Transmission Type")
    vin_no = fields.Char(string="VIN Number", translate=True)

    @api.model
    def default_get(self, field):
        res = super(BookingVehicleDetails, self).default_get(field)
        res['vehicle_booking_id'] = self._context.get('active_id')
        res['customer_id'] = self._context.get('customer_id')
        return res

    @api.onchange('fleet_vehicle_id', 'vehicle_type')
    def get_fleet_vehicle_details(self):
        for rec in self:
            if rec.fleet_vehicle_id and rec.vehicle_type == 'fleet_vehicle':
                rec.vehicle_brand_id = rec.fleet_vehicle_id.vehicle_brand_id.id
                rec.vehicle_model_id = rec.fleet_vehicle_id.vehicle_model_id.id
                rec.vehicle_fuel_type_id = rec.fleet_vehicle_id.vehicle_fuel_type_id.id
                rec.transmission_type = rec.fleet_vehicle_id.transmission_type
                rec.registration_no = rec.fleet_vehicle_id.license_plate
                rec.vin_no = rec.fleet_vehicle_id.vin_no
            else:
                rec.transmission_type = ''
                rec.registration_no = ''
                rec.vin_no = ''
                rec.vehicle_brand_id = False
                rec.vehicle_model_id = False
                rec.vehicle_fuel_type_id = False

    @api.onchange('register_vehicle_id', 'vehicle_type')
    def get_register_vehicle_details(self):
        for rec in self:
            if rec.register_vehicle_id and rec.vehicle_type == 'customer_vehicle':
                rec.vehicle_brand_id = rec.register_vehicle_id.vehicle_brand_id.id
                rec.vehicle_model_id = rec.register_vehicle_id.vehicle_model_id.id
                rec.vehicle_fuel_type_id = rec.register_vehicle_id.vehicle_fuel_type_id.id
                rec.transmission_type = rec.register_vehicle_id.transmission_type
                rec.registration_no = rec.register_vehicle_id.registration_no
                rec.vin_no = rec.register_vehicle_id.vin_no
            else:
                rec.transmission_type = ''
                rec.registration_no = ''
                rec.vin_no = ''
                rec.vehicle_brand_id = False
                rec.vehicle_model_id = False
                rec.vehicle_fuel_type_id = False

    def action_add_vehicle_details(self):
        rec = self._context.get('active_id')
        vehicle_booking_id = self.env['vehicle.booking'].browse(rec)
        data = {
            'vehicle_brand_id': self.vehicle_brand_id.id,
            'vehicle_model_id': self.vehicle_model_id.id,
            'vehicle_fuel_type_id': self.vehicle_fuel_type_id.id,
            'registration_no': self.registration_no,
            'vin_no': self.vin_no,
            'transmission_type': self.transmission_type,
        }
        vehicle_booking_id.write(data)
        if self.vehicle_type == 'customer_vehicle' and not self.register_vehicle_id:
            data['customer_id'] = self.customer_id.id
            self.env['register.vehicle'].create(data)
