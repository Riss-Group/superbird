from odoo import models, api, fields
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def _action_done(self):
        '''
            Override of base picking _action done
            First we filter all of the moves in which the product is configured to use auto landed cost
            Then we create the landed cost dictionary with 0 value for the LC products configured
            The landed cost is then created
            Afterwards we need to make our own computation instead of the base compute landed cost function.
            Write the move specific valuation adjustment that is portioned out
            After this is written we sum out all of the valuation adjustments per LC product and update the cost lines to match
            Finally validate the Landed cost
        '''
        super()._action_done()
        for picking in self:
            additional_costs_dicts = []
            lc_moves = picking.move_ids.filtered(lambda x: x.product_id.product_landed_cost_lines and x.product_id.categ_id.property_cost_method != 'standard')
            if not lc_moves:
                return
            if not picking.company_id.auto_landed_cost_account_id:
                raise ValidationError(f"For picking [{picking.name}] the company [{picking.company_id.name}] does not have a proper Landed Cost Account set up in the settings under the Accounting block.\
                    \nPlease configure it since this picking requires it")
            if not picking.company_id.lc_journal_id:
                raise ValidationError(f"For picking [{picking.name}] a default journal for Landed Costs is not configured in the Inventory Settings page for {picking.company_id.name}")
            for product_id in lc_moves.product_id.product_landed_cost_lines.mapped('landed_cost_product'):
                additional_costs_dicts.append((0, 0, {
                    'product_id': product_id.id,
                    'split_method': 'equal',
                    'price_unit': 0,
                    'name': product_id.name,
                    'account_id': picking.company_id.auto_landed_cost_account_id.id
                }))            
            if additional_costs_dicts:
                landed_cost_vals = {
                    'date': fields.Date.today(),
                    'picking_ids': [(6, 0, picking.ids)],
                    'cost_lines': additional_costs_dicts,
                    'account_journal_id': picking.company_id.lc_journal_id.id,
                    'target_model': 'picking'
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
                            'quantity': move.quantity,
                            'move_id': move.id
                        }))
                landed_cost_id.write({'valuation_adjustment_lines': valuation_adjustment_lines_vals})
                for additional_cost in landed_cost_id.cost_lines:
                    additional_cost.price_unit = sum(landed_cost_id.valuation_adjustment_lines.filtered(lambda x:x.cost_line_id == additional_cost).mapped('additional_landed_cost'))
                landed_cost_id.button_validate()