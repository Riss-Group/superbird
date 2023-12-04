# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class VehicleServiceType(models.Model):
    """Vehicle Service Type"""
    _inherit = 'product.product'
    _description = __doc__

    color = fields.Integer(default=1)
    is_vehicle_part = fields.Boolean(string="Vehicle Spare Part")


class VehicleSparePart(models.Model):
    """Vehicle Spare part"""
    _name = 'vehicle.spare.part'
    _description = __doc__
    _rec_name = 'product_id'

    color = fields.Integer()
    product_id = fields.Many2one('product.product', domain="[('is_vehicle_part', '=', True)]",
                                 required=True, string='Spare Part')
    qty = fields.Integer(string="Quantity", default=1)
    unit_price = fields.Monetary(string="Unit Price")
    sub_total = fields.Monetary(string="Sub Total", compute='_get_part_sub_total')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    inspection_job_card_id = fields.Many2one('inspection.job.card')

    @api.onchange('product_id')
    def vehicle_spare_part_price(self):
        for rec in self:
            if rec.product_id:
                rec.unit_price = rec.product_id.lst_price

    @api.depends('qty', 'unit_price')
    def _get_part_sub_total(self):
        for rec in self:
            rec.sub_total = rec.qty * rec.unit_price


class VehicleOrderSparePart(models.Model):
    """Vehicle Order Spare part"""
    _name = 'vehicle.order.spare.part'
    _description = __doc__
    _rec_name = 'product_id'

    color = fields.Integer()
    product_id = fields.Many2one('product.product', domain="[('is_vehicle_part', '=', True)]",
                                 required=True, string='Spare Part')
    qty = fields.Integer(string="Quantity", default=1)
    unit_price = fields.Monetary(string="Unit Price")
    sub_total = fields.Monetary(string="Sub Total", compute='_get_part_sub_total')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    repair_job_card_id = fields.Many2one('repair.job.card')

    @api.onchange('product_id')
    def vehicle_spare_part_price(self):
        for rec in self:
            if rec.product_id:
                rec.unit_price = rec.product_id.lst_price

    @api.depends('qty', 'unit_price')
    def _get_part_sub_total(self):
        for rec in self:
            rec.sub_total = rec.qty * rec.unit_price
