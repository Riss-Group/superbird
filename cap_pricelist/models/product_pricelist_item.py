# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"


    applied_on = fields.Selection(selection_add=[('4_public_category', 'Public Category'),('5_vendor', 'Vendor')], default='3_global',
                                  ondelete={'4_public_category': 'set default','5_vendor': 'set default'})

    vendor_id = fields.Many2one('res.partner', 'Vendor', domain=lambda self: self._get_vendor_domain())

    public_categ_id = fields.Many2one(
        string="Public Category",
        comodel_name='product.public.category',
    )

    def _get_vendor_domain(self):
        partner_ids = self.env['product.supplierinfo'].search([]).mapped('partner_id.id')
        return [('id', 'in', partner_ids)]

    def _is_applicable_for(self, product, qty_in_product_uom):
        res = super(PricelistItem, self)._is_applicable_for(product, qty_in_product_uom)

        if self.applied_on == "4_public_category":
            if (
                self.public_categ_id.id not in product.public_categ_ids.ids
                and not any(public_categ.parent_path.startswith(self.public_categ_id.parent_path) for public_categ in product.public_categ_ids)
            ):
                res = False
        elif self.applied_on == "5_vendor":
            vendor = self.env.context.get('partner_id')
            if self.vendor_id != vendor:
                res = False
        return res
