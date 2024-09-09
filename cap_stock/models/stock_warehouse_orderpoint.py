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


    formula_type = fields.Selection([('fixed','Fixed'), ('python_code', 'Python Code')], default='fixed')
    python_code_id = fields.Many2one('reordering.rule.python.code', string='Python Code')
    last_min_max_run_date = fields.Datetime()
    show_run_min_max = fields.Boolean(compute="_compute_show_run_min_max")


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
            if record.formula_type == 'python_code' and record.python_code_id.python_code:
                eval_context = record._get_eval_context()
                res = safe_eval(record.python_code_id.python_code, eval_context, mode='exec', nocopy=True)
                vals = {'last_min_max_run_date' :fields.Datetime.now()}
                record.write(vals)
    
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
            'Math': wrap_module(math, dir(math))
        })
        return eval_context

    def _set_auto_min_max_variable_data(self, warehouse_id=False):
        '''
            Populate reordering rule values from the warehouse.

            return vals_dict to write
        '''
        return {
                'python_code_id': warehouse_id.python_code_id.id if warehouse_id else False,
                'formula_type': warehouse_id.formula_type if warehouse_id else 'fixed'
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
            ('python_code_id.python_code', '!=', False)
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