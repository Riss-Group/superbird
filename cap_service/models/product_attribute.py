from odoo import models, fields, api
from odoo.exceptions import UserError


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    is_cap = fields.Boolean(string="CAP Attribute")
    is_bu = fields.Boolean(string="BU Attribute")

class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    company_code = fields.Char()

class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    company_code = fields.Char(related="product_attribute_value_id.company_code", store=True)