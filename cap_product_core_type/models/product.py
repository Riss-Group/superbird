# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    has_core = fields.Boolean("Has Core Part")
    is_core_type = fields.Boolean("is Core")

    @api.onchange("is_core_type")
    def _onchange_is_core_type(self):
        if self.is_core_type :
            core_part_categ = self.env.ref("cap_product_core_type.core_part_categ")
            self.write({
                'sale_ok': False,
                'purchase_ok': False,
                'categ_id': core_part_categ.id,
                        })


class ProductProduct(models.Model):
    _inherit = 'product.product'

    has_core = fields.Boolean(related="product_tmpl_id.has_core", string="Has Core Part", readonly=False)
    is_core_type = fields.Boolean(related="product_tmpl_id.is_core_type", string="Is Core", readonly=False)
    core_part_id = fields.Many2one('product.product', string="Core Part", domain="[('id','!=',id)]")

    @api.onchange("is_core_type")
    def _onchange_is_core_type(self):
        if self.is_core_type :
            core_part_categ = self.env.ref("cap_product_core_type.core_part_categ")
            self.write({
                'sale_ok': False,
                'purchase_ok': False,
                'categ_id': core_part_categ.id,
                        })
