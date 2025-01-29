from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    interco_sale_line_id = fields.Many2one('sale.order.line', string='Intercompany Sale Line')

    #Todo: take into account currency conversion
    # def write(self, vals):
    #     # On PO price modification sync that price to the interco SO line
    #     res = super().write(vals)
    #     if 'price_unit' in vals and vals['price_unit'] != 0:
    #         for rec in self.sudo().filtered(lambda x: x.interco_sale_line_id and x.interco_sale_line_id.price_unit != vals['price_unit']):
    #             rec.interco_sale_line_id.price_unit = vals['price_unit']
    #     return res
    #
    # @api.model_create_multi
    # def create(self, vals_list):
    #     # On PO creation if the interco SO line has no price set it the same as the PO
    #     records = super().create(vals_list)
    #     for rec in records.sudo().filtered(lambda x: x.interco_sale_line_id and x.interco_sale_line_id.price_unit != x.price_unit and x.price_unit != 0):
    #         rec.interco_sale_line_id.price_unit = rec.price_unit
    #     return records