from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    interco_purchase_line_id = fields.Many2one('purchase.order.line', string='Intercompany Purchase Line')

    #Todo: take into account currency conversion
    def write(self, vals):
        res = super().write(vals)
        if 'price_unit' in vals and vals['price_unit'] != 0:
            for rec in self.sudo().filtered(lambda x: x.interco_purchase_line_id and x.interco_purchase_line_id.price_unit != vals['price_unit']):
                rec.interco_purchase_line_id.price_unit = vals['price_unit']
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records.sudo().filtered(lambda x: x.interco_purchase_line_id and x.interco_purchase_line_id.price_unit != x.price_unit and x.price_unit != 0):
            rec.interco_purchase_line_id.price_unit = rec.price_unit
        return records