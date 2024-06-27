from odoo import models, api, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def _action_done(self):
        super()._action_done()
        for picking in self:
            additional_costs_dicts = []
            lc_moves = picking.move_ids.filtered(lambda x: x.product_id.product_landed_cost_lines and x.product_id.categ_id.property_cost_method != 'standard')
            for product_id in lc_moves.product_id.product_landed_cost_lines.mapped('landed_cost_product'):
                additional_costs_dicts.append((0, 0, {
                    'product_id': product_id.id,
                    'split_method': 'equal',
                    'price_unit': 0,
                    'name': product_id.name
                }))            
            if additional_costs_dicts:
                landed_cost_vals = {
                    'date': fields.Date.today(),
                    'picking_ids': [(6, 0, picking.ids)],
                    'cost_lines': additional_costs_dicts,
                }
                landed_cost_id = self.env['stock.landed.cost'].create(landed_cost_vals)
                valuation_adjustment_lines_vals = []
                for move in lc_moves:
                    move_total_cost = move._get_price_unit()
                    for landed_cost_product in move.product_id.product_landed_cost_lines:
                        cost_line = landed_cost_id.cost_lines.filtered(lambda x: x.product_id == landed_cost_product.landed_cost_product)
                        valuation_adjustment_lines_vals.append((0,0,{
                            'cost_line_id': cost_line[0].id,
                            'product_id': move.product_id.id,
                            'former_cost': move_total_cost * move.quantity,
                            'additional_landed_cost': move_total_cost * landed_cost_product.percentage * move.quantity,
                            'quantity': move.quantity
                        }))
                landed_cost_id.write({'valuation_adjustment_lines': valuation_adjustment_lines_vals})
                for additional_cost in landed_cost_id.cost_lines:
                    additional_cost.price_unit = sum(landed_cost_id.valuation_adjustment_lines.filtered(lambda x:x.cost_line_id == additional_cost).mapped('additional_landed_cost'))
                landed_cost_id.button_validate()