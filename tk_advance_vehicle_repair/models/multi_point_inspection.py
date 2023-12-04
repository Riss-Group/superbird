# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class VehicleComponent(models.Model):
    """Vehicle Component"""
    _name = "vehicle.component"
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, translate=True)
    compo_vehicle_side = fields.Selection([('top_side', "Top Side"), ('bottom_side', "Bottom Side")],
                                          string="Vehicle Side", required=True)


class VehicleFluid(models.Model):
    """Vehicle Fluid"""
    _name = "vehicle.fluid"
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, translate=True)
    fluid_vehicle_side = fields.Selection([('top_side', "Top Side"), ('bottom_side', "Bottom Side")],
                                          string="Vehicle Side", required=True)


class VehicleComponents(models.Model):
    """Vehicle Components"""
    _name = "vehicle.components"
    _description = __doc__
    _rec_name = 'vehicle_component_id'

    avatar = fields.Binary(string="Image")
    vehicle_component_id = fields.Many2one('vehicle.component', string="Component",
                                           domain="[('compo_vehicle_side', '=', c_vehicle_side)]", required=True)
    c_vehicle_side = fields.Selection([('top_side', "Top Side"), ('bottom_side', "Bottom Side")], string="Vehicle Side",
                                      required=True)
    condition = fields.Selection([('require_future_attention', "Require Future Attention"),
                                  ('require_immediate_attention', "Require Immediate Attention"),
                                  ('checked_ok', "Checked and Okay at this Time")], string="Present Condition")
    remarks = fields.Char(string="Remarks", translate=True)
    inspection_job_card_id = fields.Many2one('inspection.job.card')


class VehicleFluids(models.Model):
    """Vehicle Fluids"""
    _name = "vehicle.fluids"
    _description = __doc__
    _rec_name = 'vehicle_fluid_id'

    avatar = fields.Binary(string="Image")
    vehicle_fluid_id = fields.Many2one('vehicle.fluid', string="Fluid",
                                       domain="[('fluid_vehicle_side', '=', f_vehicle_side)]", required=True)
    f_vehicle_side = fields.Selection([('top_side', "Top Side"), ('bottom_side', "Bottom Side")], string="Vehicle Side",
                                      required=True)
    condition = fields.Selection([('require_future_attention', "Require Future Attention"),
                                  ('require_immediate_attention', "Require Immediate Attention"),
                                  ('checked_ok', "Checked and Okay at this Time")], string="Present Condition")
    remarks = fields.Char(string="Remarks", translate=True)
    inspection_job_card_id = fields.Many2one('inspection.job.card')


class TyreInspection(models.Model):
    """Tyre Inspection"""
    _name = 'tyre.inspection'
    _description = __doc__
    _rec_name = 'tyre'

    avatar = fields.Binary(string="Image")
    tyre = fields.Selection([('lf', "Left Front"), ('rf', "Right Front"), ('lr', "Left Rear"), ('rr', "Right Rear")],
                            string="Tyre Location", required=True)
    tread_wear = fields.Char(string="Tread Wear", translate=True)
    tread_depth = fields.Char(string="Tread Depth", translate=True)
    tyre_pressure = fields.Char(string="Tyre Pressure", translate=True)
    brake_pads = fields.Float(string="Brake pads (%)")
    condition = fields.Selection([('require_future_attention', "Require Future Attention"),
                                  ('require_immediate_attention', "Require Immediate Attention"),
                                  ('checked_ok', "Checked and Okay at this Time")], string="Present Condition")
    inspection_job_card_id = fields.Many2one('inspection.job.card')
