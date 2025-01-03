# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    description = fields.Char(string="Attribute description")
    manufacturer = fields.Char(string="Manufacturer")
    chassis_model = fields.Char(string="Chassis Model")
    chassis_model_number = fields.Char(string="Chassis Model Number")
    option_number = fields.Char(string="Option Number")
    option_name = fields.Char(string="Option Name")
