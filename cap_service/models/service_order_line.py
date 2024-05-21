from odoo import models, fields, api
from odoo.exceptions import UserError


class ServiceOrderLine(models.Model):
    _name = 'service.order.line'

    sequence = fields.Integer()
    name = fields.Char(string='Description')
    cause = fields.Char(compute="_compute_cause_correction", store=True, readonly=False)
    correction = fields.Char(compute="_compute_cause_correction", store=True, readonly=False)
    service_order_id = fields.Many2one('service.order')
    project_id = fields.Many2one('project.project')
    task_ids = fields.Many2many('project.task', related='service_order_line_labor_ids.task_ids')
    # task_stage_ids = fields.Many2many('project.task.type', related='task_ids.stage_id', store=True, readonly=True)
    user_ids = fields.Many2many('res.users', related='task_ids.user_ids', readonly=False)
    hours = fields.Float(string="Hours(est)", compute='_compute_hours')
    hours_consumed = fields.Float(string="Hours(consumed)", compute="_compute_hours_consumed")
    service_order_line_product_ids = fields.One2many('service.order.line.product', 'service_order_line_id')
    ttype = fields.Selection([
        ('Customer','Customer'),
        ('Internal','Internal'),
        ('Warranty','Warranty'),
    ],default='Customer')
    subtotal = fields.Float(compute="_compute_subtotal")
    service_order_line_item_ids = fields.One2many('service.order.line.product', 'service_order_line_id',
                                                  domain=[('product_type', '=', 'product')], string="Items")
    service_order_line_labor_ids = fields.One2many('service.order.line.product', 'service_order_line_id',
                                                   domain=[('product_type', '=', 'service')], string="Labor")

    @api.depends('task_ids.timesheet_ids.unit_amount')
    def _compute_hours_consumed(self):
        for record in self:
            record.hours_consumed = sum(record.mapped('task_ids.timesheet_ids.unit_amount'))

    @api.depends('service_order_line_labor_ids.quantity')
    def _compute_hours(self):
        for record in self:
            record.hours = sum(record.service_order_line_labor_ids.mapped('quantity'))

    @api.depends('service_order_line_product_ids.quantity', 'service_order_line_product_ids.unit_price')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = sum([x.quantity * x.unit_price for x in record.service_order_line_product_ids])

    @api.depends('task_ids.cause', 'task_ids.correction')
    def _compute_cause_correction(self):
        for record in self:
            record.cause = '\n'.join([x for x in record.mapped('task_ids.cause') if x])
            record.correction = '\n'.join([x for x in record.mapped('task_ids.correction') if x])

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
                'service_order_line_id': self.id,
            },
            'target': 'new',
        }