from odoo import  models, fields, api
from odoo.exceptions import UserError


class ServiceOrderLineService(models.Model):
    _name = 'service.order.line.service'  
    _description = 'Service Order Line Service' 

    service_order_line_id = fields.Many2one('service.order.line', ondelete='cascade')    
    sale_line_id = fields.One2many('sale.order.line', 'service_order_line_service_id')
    invoice_line_ids = fields.One2many('account.move.line', 'service_order_line_service_id')
    qty_to_invoice = fields.Float(compute='_compute_qty_invoice', store=True, readonly=False)
    qty_invoiced = fields.Float(compute='_compute_qty_invoice', store=True, readonly=False)
    product_id = fields.Many2one('product.product')
    product_name = fields.Char()
    quantity = fields.Float(digits='Product Unit of Measure')
    quantity_consumed = fields.Float(compute="_compute_quantity_consumed", store=True, readonly=True, digits='Product Unit of Measure')
    unit_price = fields.Float()
    subtotal = fields.Float(compute='_compute_subtotal', store=True, readonly=False)

    def _compute_display_name(self):
        super()._compute_display_name()
        for record in self:
            record.display_name = f"{record.product_id.name}"

    @api.depends('quantity', 'quantity_consumed', 'invoice_line_ids.quantity',  'invoice_line_ids.move_id.state', 'service_order_line_id.bill_type')
    def _compute_qty_invoice(self):
        for record in self:
            qty = record.quantity if record.service_order_line_id.bill_type == 'estimate' else record.quantity_consumed
            qty_invoiced = sum( record.invoice_line_ids.filtered(lambda x: x.move_id.state != 'cancel').mapped('quantity'))
            record.qty_invoiced = qty_invoiced
            record.qty_to_invoice = qty - qty_invoiced

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            record.unit_price = record.product_id.list_price
            record.product_name = record.product_id.display_name
    
    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.quantity * record.unit_price

    @api.depends('service_order_line_id.task_id.timesheet_ids.unit_amount', 'service_order_line_id.task_id.timesheet_ids.service_labor_product_id')
    def _compute_quantity_consumed(self):
        for record in self:
            timesheet_ids = record.service_order_line_id.task_id.timesheet_ids.filtered(lambda x: x.service_labor_product_id == record.product_id)
            record.quantity_consumed = sum(timesheet_ids.mapped('unit_amount'))

    def button_view_services(self):
        return self.service_order_line_id.button_view_services()
    
    def write(self, vals):
        if 'service_order_line_id' in vals and not vals['service_order_line_id']:
            self.unlink()
            return True
        return super().write(vals)