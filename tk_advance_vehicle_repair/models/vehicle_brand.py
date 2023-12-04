# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class VehicleBrand(models.Model):
    """Vehicle Brand"""
    _name = 'vehicle.brand'
    _description = __doc__
    _rec_name = 'name'

    avatar = fields.Binary(string="Avatar")
    name = fields.Char(string="Name", required=True, translate=True)


class VehicleModel(models.Model):
    """Vehicle Model"""
    _name = 'vehicle.model'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, translate=True)
    vehicle_brand_id = fields.Many2one('vehicle.brand', string="Vehicle Brand", required=True)
