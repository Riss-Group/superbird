# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class VehicleBooking(models.Model):
    """Vehicle Booking"""
    _name = 'vehicle.booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'booking_number'

    booking_number = fields.Char(string='Booking No', readonly=True, default=lambda self: _('New'), copy=False)
    booking_date = fields.Date(string="Booking Date", )
    vehicle_brand_id = fields.Many2one('vehicle.brand', string="Vehicle", )
    vehicle_model_id = fields.Many2one('vehicle.model', string="Model",
                                       domain="[('vehicle_brand_id', '=', vehicle_brand_id)]", )
    vehicle_fuel_type_id = fields.Many2one('vehicle.fuel.type', string="Fuel Type", )
    registration_no = fields.Char(string="Registration No", translate=True)
    vin_no = fields.Char(string="VIN No", translate=True)
    transmission_type = fields.Selection([('manual', "Manual"), ('automatic', "Automatic"), ('cvt', "CVT")],
                                         string="Transmission Type")

    customer_id = fields.Many2one('res.partner', string='Customer', )
    street = fields.Char(string="Street", translate=True)
    street2 = fields.Char(string="Street 2", translate=True)
    city = fields.Char(string="City", translate=True)
    state_id = fields.Many2one("res.country.state", string="State")
    country_id = fields.Many2one("res.country", string="Country")
    zip = fields.Char(string="Zip")
    phone = fields.Char(string="Phone", translate=True)
    email = fields.Char(string="Email", translate=True)
    customer_observation = fields.Text(string="Customer Observation", translate=True)
    responsible_id = fields.Many2one('res.users', default=lambda self: self.env.user, required=True,
                                     string="Responsible")

    booking_source = fields.Selection([('direct', "Direct"), ('website', "Website")], string="Booking Source")
    booking_type = fields.Selection(
        [('only_inspection', "Only Vehicle Inspection"), ('only_repair', "Only Vehicle Repair"),
         ('inspection_and_repair', "Vehicle Inspection + Vehicle Repair")], string="Booking Type",
        default='only_inspection')

    estimate_cost = fields.Monetary(string="Estimate Cost")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")

    vehicle_service_ids = fields.Many2many('vehicle.service', string="Services")
    vehicle_spare_part_ids = fields.Many2many('product.product', domain="[('is_vehicle_part', '=', True)]",
                                              string='Spare Parts')

    inspection_job_card_id = fields.Many2one('inspection.job.card', string="Inspection Job Card")
    repair_job_card_id = fields.Many2one('repair.job.card', string="Repair Job Card")

    booking_stages = fields.Selection(
        [('draft', "New"), ('vehicle_inspection', "Vehicle Inspection"), ('vehicle_repair', "Vehicle Repair"),
         ('vehicle_inspection_repair', "Inspection + Repair"), ('cancel', "Cancel")], default='draft', string="Stages",
        group_expand='_expand_groups')

    register_vehicle_id = fields.Many2one('register.vehicle', string="Registered Vehicle",
                                          domain="[('customer_id', '=', customer_id)]")

    @api.model
    def _expand_groups(self, states, domain, order):
        return ['draft', 'vehicle_inspection', 'vehicle_repair', 'vehicle_inspection_repair', 'cancel']

    def draft_to_vehicle_inspection(self):
        if not self.vehicle_brand_id or not self.registration_no or not self.vehicle_model_id or not self.vehicle_fuel_type_id:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _("Required: Vehicle, Registration No, Model, and Fuel Type for mandatory information."),
                    'sticky': False,
                }
            }
            return message
        data = {
            "vehicle_brand_id": self.vehicle_brand_id.id,
            "vehicle_model_id": self.vehicle_model_id.id,
            "inspection_date": self.booking_date,
            "vehicle_fuel_type_id": self.vehicle_fuel_type_id.id,
            "registration_no": self.registration_no,
            "vin_no": self.vin_no,
            "transmission_type": self.transmission_type,
            "customer_id": self.customer_id.id,
            "street": self.street,
            "street2": self.street2,
            "city": self.city,
            "state_id": self.state_id.id,
            "country_id": self.country_id.id,
            "zip": self.zip,
            "phone": self.phone,
            "email": self.email,
            "inspect_type": self.booking_type,
        }
        inspection_job_card_id = self.env['inspection.job.card'].create(data)
        self.inspection_job_card_id = inspection_job_card_id.id
        self.booking_stages = 'vehicle_inspection'
        return {
            'type': 'ir.actions.act_window',
            'name': _('Inspection Job Card'),
            'res_model': 'inspection.job.card',
            'res_id': inspection_job_card_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def vehicle_inspection_to_vehicle_repair(self):
        if not self.vehicle_brand_id or not self.registration_no or not self.vehicle_model_id or not self.vehicle_fuel_type_id:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _("Required: Vehicle, Registration No, Model, and Fuel Type for mandatory information."),
                    'sticky': False,
                }
            }
            return message
        data = {
            "vehicle_brand_id": self.vehicle_brand_id.id,
            "vehicle_model_id": self.vehicle_model_id.id,
            "inspect_repair_date": self.booking_date,
            "vehicle_fuel_type_id": self.vehicle_fuel_type_id.id,
            "registration_no": self.registration_no,
            "vin_no": self.vin_no,
            "transmission_type": self.transmission_type,
            "customer_id": self.customer_id.id,
            "street": self.street,
            "street2": self.street2,
            "city": self.city,
            "state_id": self.state_id.id,
            "country_id": self.country_id.id,
            "zip": self.zip,
            "phone": self.phone,
            "email": self.email,
        }
        repair_job_card_id = self.env['repair.job.card'].create(data)
        self.repair_job_card_id = repair_job_card_id.id
        self.booking_stages = 'vehicle_repair'

        for part in self.vehicle_spare_part_ids:
            part = {
                'product_id': part.id,
                'unit_price': part.lst_price,
                'repair_job_card_id': repair_job_card_id.id,
            }
            self.env['vehicle.order.spare.part'].create(part)

        for service in self.vehicle_service_ids:
            service = {
                'vehicle_service_id': service.id,
                'service_charge': service.service_charge,
                'repair_job_card_id': repair_job_card_id.id
            }
            self.env['vehicle.service.team'].create(service)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Repair Job Card'),
            'res_model': 'repair.job.card',
            'res_id': repair_job_card_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def vehicle_repair_to_vehicle_inspection_repair(self):
        if not self.vehicle_brand_id or not self.registration_no or not self.vehicle_model_id or not self.vehicle_fuel_type_id:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _("Required: Vehicle, Registration No, Model, and Fuel Type for mandatory information."),
                    'sticky': False,
                }
            }
            return message
        data = {
            "vehicle_brand_id": self.vehicle_brand_id.id,
            "vehicle_model_id": self.vehicle_model_id.id,
            "inspection_date": self.booking_date,
            "vehicle_fuel_type_id": self.vehicle_fuel_type_id.id,
            "registration_no": self.registration_no,
            "vin_no": self.vin_no,
            "transmission_type": self.transmission_type,
            "customer_id": self.customer_id.id,
            "street": self.street,
            "street2": self.street2,
            "city": self.city,
            "state_id": self.state_id.id,
            "country_id": self.country_id.id,
            "zip": self.zip,
            "phone": self.phone,
            "email": self.email,
            "inspect_type": self.booking_type,
        }
        inspection_job_card_id = self.env['inspection.job.card'].create(data)
        self.inspection_job_card_id = inspection_job_card_id.id
        self.booking_stages = 'vehicle_inspection_repair'

        for s_part in self.vehicle_spare_part_ids:
            s_part = {
                'product_id': s_part.id,
                'unit_price': s_part.lst_price,
                'inspection_job_card_id': inspection_job_card_id.id,
            }
            self.env['vehicle.spare.part'].create(s_part)

        for s_service in self.vehicle_service_ids:
            s_service = {
                'vehicle_service_id': s_service.id,
                'service_charge': s_service.service_charge,
                'inspection_job_card_id': inspection_job_card_id.id
            }
            self.env['inspection.repair.team'].create(s_service)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Inspection Job Card'),
            'res_model': 'inspection.job.card',
            'res_id': inspection_job_card_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def vehicle_inspection_repair_to_cancel(self):
        self.booking_stages = 'cancel'

    @api.constrains('vehicle_fuel_type_id')
    def _vehicle_fuels(self):
        for record in self:
            if not record.vehicle_fuel_type_id:
                raise ValidationError("Please, add fuel type")

    @api.onchange('customer_id')
    def customer_details(self):
        for rec in self:
            if rec.customer_id:
                rec.phone = rec.customer_id.phone
                rec.email = rec.customer_id.email
                rec.street = rec.customer_id.street
                rec.street2 = rec.customer_id.street2
                rec.city = rec.customer_id.city
                rec.state_id = rec.customer_id.state_id
                rec.country_id = rec.customer_id.country_id
                rec.zip = rec.customer_id.zip

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('booking_number', _('New')) == _('New'):
                vals['booking_number'] = self.env['ir.sequence'].next_by_code('vehicle.booking') or _('New')
        res = super(VehicleBooking, self).create(vals_list)
        return res
