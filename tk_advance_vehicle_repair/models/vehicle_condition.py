# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class VehicleConditionLocation(models.Model):
    """Vehicle Condition Location"""
    _name = "vehicle.condition.location"
    _description = __doc__
    _rec_name = 'location'

    location = fields.Char(string="Location", required=True, translate=True)


class VehicleCondition(models.Model):
    """Vehicle Condition"""
    _name = "vehicle.condition"
    _description = __doc__
    _rec_name = 'condition'

    condition = fields.Char(string="Condition", required=True, translate=True)
    condition_code = fields.Char(string="Condition Code", translate=True)


class VehicleConditionLine(models.Model):
    """Vehicle Condition Line"""
    _name = "vehicle.condition.line"
    _description = __doc__
    _rec_name = 'vehicle_view'

    avatar = fields.Binary(string="Image")
    vehicle_view = fields.Selection([('top', "Top View"), ('bottom', "Bottom View"), ('left_side', "Left Side View"),
                                     ('right_side', "Right Side View"), ('front', "Front View"), ('back', "Back View")],
                                    string="Vehicle View", required=True)
    vehicle_condition_location_id = fields.Many2one('vehicle.condition.location', string="Location", required=True)
    vehicle_condition_id = fields.Many2one('vehicle.condition', string="Condition", required=True)
    condition_code = fields.Char(string="Condition Code", translate=True)
    inspection_job_card_id = fields.Many2one('inspection.job.card')

    @api.onchange('vehicle_condition_id')
    def get_condition_description(self):
        for rec in self:
            if rec.vehicle_condition_id:
                rec.condition_code = rec.vehicle_condition_id.condition_code


class VehicleItem(models.Model):
    """Vehicle Item"""
    _name = "vehicle.item"
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, translate=True)
    item_category = fields.Selection([('mechanical', "Mechanical Item"), ('interior', "Interior Item")],
                                     required=True, string="Category")


class MechanicalItemCondition(models.Model):
    """Mechanical Item Condition"""
    _name = "mechanical.item.condition"
    _description = __doc__
    _rec_name = 'vehicle_item_id'

    avatar = fields.Binary(string="Image")
    vehicle_item_id = fields.Many2one('vehicle.item', string="Name", required=True,
                                      domain="[('item_category', '=', 'mechanical')]")
    mechanical_condition = fields.Selection([('poor', "Poor"), ('average', "Average"),
                                             ('not_working', "Not Working"), ('good', "Good"), ('other', "Other")],
                                            string="Condition")
    mechanical_condition_notes = fields.Char(string="Remarks", translate=True)
    inspection_job_card_id = fields.Many2one('inspection.job.card')


class InteriorItemCondition(models.Model):
    """Interior Item Condition"""
    _name = "interior.item.condition"
    _description = __doc__
    _rec_name = 'vehicle_item_id'

    avatar = fields.Binary(string="Image")
    vehicle_item_id = fields.Many2one('vehicle.item', string="Name", required=True,
                                      domain="[('item_category', '=', 'interior')]")
    interior_condition = fields.Selection([('worn', "Worn"), ('burnt', "Burnt"), ('ripped', "Ripped"),
                                           ('good', "Good"), ('other', "Other")], string="Condition")
    interior_condition_notes = fields.Char(string="Remarks", translate=True)
    inspection_job_card_id = fields.Many2one('inspection.job.card')
