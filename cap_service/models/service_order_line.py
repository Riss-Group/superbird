from odoo import  models, fields, api
from odoo import  models, fields, api
from odoo.exceptions import UserError


class ServiceOrder(models.Model):
    _name = 'service.order.line'
    _description = "Service Order Line"
    

    name = fields.Text(string='Description')
    cause = fields.Text(compute="_compute_cause_correction", store=True, readonly=False)
    correction = fields.Text(compute="_compute_cause_correction", store=True, readonly=False)
    project_id = fields.Many2one('project.project', copy=False)
    task_id = fields.Many2one('project.task', copy=False)
    task_stage = fields.Many2one('project.task.type', related='task_id.stage_id', store=True, readonly=True)
    user_ids = fields.Many2many('res.users', related='task_id.user_ids', readonly=False)
    hours = fields.Float(string="Hours(est)", compute='_compute_hours')
    hours_consumed = fields.Float(string="Hours(consumed)", compute="_compute_hours_consumed")
    ttype = fields.Selection([
        ('Customer','Customer'),
        ('Internal','Internal'),
        ('Warranty','Warranty'),
    ],default='Customer', required=True)
    subtotal = fields.Float(compute="_compute_subtotal")
    service_order_id = fields.Many2one('service.order', ondelete='cascade')
    sale_line_ids = fields.One2many('sale.order.line', 'service_order_line_id')
    service_order_line_product_ids = fields.One2many('service.order.line.product', 'service_order_line_id',)
    service_order_line_service_ids = fields.One2many('service.order.line.service', 'service_order_line_id',)
    sequence = fields.Integer()
    
    
    @api.depends('task_id.timesheet_ids.unit_amount')
    def _compute_hours_consumed(self):
        for record in self:
            record.hours_consumed = sum(record.task_id.timesheet_ids.mapped('unit_amount'))
    
    @api.depends('service_order_line_service_ids.quantity')
    def _compute_hours(self):
        for record in self:
            record.hours = sum(record.service_order_line_service_ids.mapped('quantity'))
    
    @api.depends('service_order_line_service_ids.quantity', 'service_order_line_service_ids.unit_price', 'service_order_line_product_ids.quantity', 'service_order_line_product_ids.unit_price' )
    def _compute_subtotal(self):
        for record in self:
            subtotal = 0
            subtotal += sum([x.quantity * x.unit_price for x in record.service_order_line_product_ids])
            subtotal += sum([x.quantity * x.unit_price for x in record.service_order_line_service_ids])
            record.subtotal = subtotal
    
    @api.depends('task_id.cause', 'task_id.correction')
    def _compute_cause_correction(self):
        for record in self:
            record.cause = record.task_id.cause
            record.correction = record.task_id.correction
    
    def button_view_products(self):
        '''
            Service Line ID is passed through context

            Returns:
                Window Action
        '''
        return {
            'name': 'View/Add Products',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'service.line.view.product',
            'context': {
                'default_service_order_line_id': self.id,
                'default_ttype': 'product'
            },
            'target': 'new',
        }
    
    def button_view_services(self):
        '''
            Service Line ID is passed through context

            Returns:
                Window Action
        '''
        return {
            'name': 'View/Add Services',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'service.line.view.product',
            'context': {
                'default_service_order_line_id': self.id,
                'default_ttype': 'service'
            },
            'target': 'new',
        }