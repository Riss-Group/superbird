from odoo import models, api, fields

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'


    formula_type = fields.Selection([('fixed','Fixed'), ('python_code', 'Python Code')], default="fixed")
    python_code_id = fields.Many2one('reordering.rule.python.code', string='Python Code')

    def update_params_on_reordering_rules(self):
        '''
            Update the reordering rule parameters for all orderpoints associated with the locations in the current warehouse.
        '''
        for record in self:
            location_ids = self.env['stock.location'].search([('warehouse_id','=',record.id)])
            stock_warehouse_orderpoint_ids = self.env['stock.warehouse.orderpoint'].search([('location_id','in',location_ids.ids)])
            if not stock_warehouse_orderpoint_ids:
                return False
            vals = stock_warehouse_orderpoint_ids._set_auto_min_max_variable_data(warehouse_id=record)
            if not vals:
                return False
            stock_warehouse_orderpoint_ids.write(vals)
