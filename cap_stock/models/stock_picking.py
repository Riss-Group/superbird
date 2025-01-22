from odoo import models, api, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for pick in res:
            if pick.purchase_id and pick.origin != pick.purchase_id.name:
                pick.origin = pick.purchase_id.name
        return res
