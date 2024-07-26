from odoo import models, api, fields
from odoo.exceptions import ValidationError, UserError 
from odoo.tools.safe_eval import safe_eval, test_python_expr, wrap_module
from odoo.addons.base.models.ir_actions import LoggerProxy
import math
import logging 
_logger = logging.getLogger()

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'


    reorder_order_cost_var = fields.Float()
    reorder_inventory_maint_cost_var = fields.Float()
    reorder_period_days = fields.Integer()
    demo_sales_volume = fields.Float()
    demo_unit_cost = fields.Float()
    demo_reorder_min = fields.Float()
    demo_reorder_max = fields.Float()
    formula_type = fields.Selection([('fixed','Fixed'), ('python_code', 'Python Code')], default="fixed")
    python_code = fields.Text(string='Python Code', )


    @api.constrains('python_code')
    def _check_python_code(self):
        '''
            Validate the syntax of the Python code in the 'python_code' field.
            Raises a ValidationError if the syntax is incorrect (AKA Unsafe Execution from Base safe_eval).S
        '''
        for record in self.sudo().filtered('python_code'):
            msg = test_python_expr(expr=record.python_code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)
    
    def run_min_max(self):
        '''
            Simulates the demo min/max vals for 'python_code' field and set the minimum and maximum quantities for the orderpoint based on the evaluation results.
        '''
        for record in self:
            if record.formula_type == 'python_code' and record.python_code:
                eval_context = record._get_eval_context()
                res = safe_eval(record.python_code, eval_context, mode='exec', nocopy=True)
                record.demo_reorder_min = eval_context.get('min_qty',0)
                record.demo_reorder_max = eval_context.get('max_qty',0)

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

    @api.model
    def _get_eval_context(self):
        """
            Prepare the context used when evaluating Python code for reordering rules.
            This includes environment variables and utility functions.
        """
        def log(message, level="info"):
            with self.pool.cursor() as cr:
                cr.execute("""
                    INSERT INTO ir_logging(create_date, create_uid, type, dbname, name, level, message, path, line, func)
                    VALUES (NOW() at time zone 'UTC', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (self.env.uid, 'server', self._cr.dbname, __name__, level, message, "python code", 'run_min_max_line(whs)', 'run_min_max_func(whs)'))

        eval_context = self.env['ir.actions.actions']._get_eval_context()
        model = self.env['stock.warehouse']
        record = model.browse(self._context['active_id'])
        eval_context.update({
            'env': self.env,
            'model': model,
            'UserError': UserError,
            'record': record,
            'log': log,
            '_logger': LoggerProxy,
            'Math': wrap_module(math, dir(math)),
            'sales_volume': record.demo_sales_volume if record else 0,
            'unit_cost': record.demo_unit_cost if record else 0,
            'period_days': record.reorder_period_days if record else 0,
            'inventory_maint_cost': record.reorder_inventory_maint_cost_var if record else 0,
            'order_cost_fixed' : record.reorder_order_cost_var if record else 0,
        })
        return eval_context