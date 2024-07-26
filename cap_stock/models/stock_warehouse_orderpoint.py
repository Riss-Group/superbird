from odoo import models, api, fields, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import safe_eval, test_python_expr, wrap_module
from odoo.addons.base.models.ir_actions import LoggerProxy
from datetime import datetime, timedelta
import math
import logging 
_logger = logging.getLogger()



class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    purchase_order_cost_var = fields.Float()
    inventory_maint_cost_var = fields.Float()
    period_days = fields.Integer()
    sales_order_line_volume = fields.Float(compute="_compute_sales_order_line_volume")
    standard_price = fields.Float(related='product_id.standard_price')
    formula_type = fields.Selection([('fixed','Fixed'), ('python_code', 'Python Code')], default='fixed')
    python_code = fields.Text(string='Python Code')
    last_min_max_run_date = fields.Datetime()
    show_run_min_max = fields.Boolean(compute="_compute_show_run_min_max")

    @api.constrains('python_code')
    def _check_python_code(self):
        '''
            Validate the syntax of the Python code in the 'python_code' field.
            Raises a ValidationError if the syntax is incorrect (AKA Unsafe Execution from Base safe_eval).
        '''
        for record in self.sudo().filtered('python_code'):
            msg = test_python_expr(expr=record.python_code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    @api.depends('period_days', 'product_id')
    def _compute_sales_order_line_volume(self):
        '''
            Compute the total volume of sales order lines for the product in the orderpoint
            within the period specified by 'period_days'.
        '''
        for record in self:
            total_volume = 0.0
            if record.product_id and record.period_days:
                date_from = datetime.today() - timedelta(days=record.period_days)
                sales_order_lines = self.env['sale.order.line'].search([
                    ('product_id', '=', record.product_id.id),
                    ('state', 'in', ['sale', 'done']), 
                    ('order_id.date_order', '>=', date_from)
                ])
                total_volume = sum(line.product_uom_qty for line in sales_order_lines)
            record.sales_order_line_volume = total_volume
    
    @api.depends('formula_type')
    def _compute_show_run_min_max(self):
        '''
            Compute function to assist with showing fields regardless of fields not exisiting due to access rights
        '''
        for record in self:
            record.show_run_min_max = record.formula_type == 'python_code'


    def run_min_max(self):
        '''
            Evaluate the Python code in the 'python_code' field and set the minimum and maximum quantities for the orderpoint based on the evaluation results.
        '''
        for record in self:
            if record.formula_type == 'python_code' and record.python_code:
                eval_context = record._get_eval_context()
                res = safe_eval(record.python_code, eval_context, mode='exec', nocopy=True)
                vals = {
                    'product_min_qty' : eval_context.get('min_qty',0),
                    'product_max_qty' : eval_context.get('max_qty',0),
                    'last_min_max_run_date' :fields.Datetime.now()
                }
                record.write(vals)
    
    def edit_min_max_formula(self):
        '''
            Return an action to open the form view for the current orderpoint to edit the minimum and maximum quantity formula.
        '''
        self.ensure_one()
        if self.id:
            return {
            'name': _('Stock Orderpoint'),
            'res_model': 'stock.warehouse.orderpoint',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
        }
    
    @api.model
    def _get_eval_context(self):
        '''
            Prepare the context used when evaluating Python code for reordering rules.
            This includes environment variables and utility functions.
        '''
        def log(message, level="info"):
            with self.pool.cursor() as cr:
                cr.execute("""
                    INSERT INTO ir_logging(create_date, create_uid, type, dbname, name, level, message, path, line, func)
                    VALUES (NOW() at time zone 'UTC', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (self.env.uid, 'server', self._cr.dbname, __name__, level, message, "python code", 'run_min_max_line', 'run_min_max_func'))
        eval_context = self.env['ir.actions.actions']._get_eval_context()
        model = self.env['stock.warehouse.orderpoint']
        record = model
        if self._context.get('active_id'):
            record = model.browse(self._context['active_id'])
        eval_context.update({
            'env': self.env,
            'model': model,
            'UserError': UserError,
            'record': record,
            'log': log,
            '_logger': LoggerProxy,
            'Math': wrap_module(math, dir(math)),
            'sales_volume': record.sales_order_line_volume if record else 0,
            'unit_cost': record.standard_price if record else 0,
            'period_days': record.period_days if record else 0,
            'inventory_maint_cost': record.inventory_maint_cost_var if record else 0,
            'order_cost_fixed' : record.purchase_order_cost_var if record else 0,
        })
        return eval_context

    def _set_auto_min_max_variable_data(self, warehouse_id=False):
        '''
            Populate reordering rule values from the warehouse.

            return vals_dict to write
        '''
        if warehouse_id:
            vals = {
                'purchase_order_cost_var': warehouse_id.reorder_order_cost_var,
                'inventory_maint_cost_var': warehouse_id.reorder_inventory_maint_cost_var,
                'period_days': warehouse_id.reorder_period_days,
                'python_code': warehouse_id.python_code,
                'formula_type': warehouse_id.formula_type
            }
            return vals
        else:
            return {
                'purchase_order_cost_var': 0,
                'inventory_maint_cost_var': 0,
                'period_days': 0,
                'python_code': False,
                'formula_type': 'fixed'
            }

    @api.model_create_multi
    def create(self, vals):
        '''
            Override create method to populate values from the warehouse.
        '''
        records = super().create(vals)
        for record in records:
            warehouse_id = record.location_id.warehouse_id
            if warehouse_id:
                auto_min_max_vals = record._set_auto_min_max_variable_data(warehouse_id=warehouse_id)
                if auto_min_max_vals:
                    record.write(auto_min_max_vals)
        return records
    
    def write(self, vals):
        '''
            Override write method to update values from the warehouse if location_id's warehouse changes.
        '''
        for record in self:
            if 'location_id' in vals:
                if vals.get('location_id'):
                    new_warehouse_id = self.env['stock.location'].browse(vals.get('location_id')).warehouse_id
                    if record.location_id.warehouse_id != new_warehouse_id:
                        vals.update(record._set_auto_min_max_variable_data(warehouse_id=new_warehouse_id))
                else:
                    vals.update(record._set_auto_min_max_variable_data())
        res = super().write(vals)
        return res
    
    @api.model
    def _cron_run_mix_max_scheduler(self, limit=250):
        '''
            Scheduled action to run the min-max calculation for orderpoints.
        
            :param limit: The maximum number of orderpoints to process in one run.
        '''
        today_start = fields.Datetime.to_string(fields.Datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
        orderpoint_ids = self.env['stock.warehouse.orderpoint'].search([
            '|', ('last_min_max_run_date', '=', False), ('last_min_max_run_date', '<', today_start),
            ('formula_type', '=', 'python_code'),
            ('python_code', '!=', False)
        ], limit=limit)
        for orderpoint_id in orderpoint_ids:
            try:
                orderpoint_id.with_context({'active_id':orderpoint_id.id}).sudo().run_min_max()
                self.env.cr.commit()
            except Exception as e:
                _logger.warning(f'Orderpoint {orderpoint_id} an exception was caught:\n\n {e}')
                self.env.cr.rollback()
        if orderpoint_ids:
            cron_job = self.env.ref('cap_stock.ir_cron_run_min_max_scheduler').sudo()
            nextcall = fields.Datetime.now() + timedelta(seconds=15)
            cron_job._trigger(at=nextcall)