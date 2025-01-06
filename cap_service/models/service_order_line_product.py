from odoo import  models, fields, api
from odoo.exceptions import UserError


class ServiceOrderLineProduct(models.Model):
    _name = 'service.order.line.product'  
    _description = 'Service Order Line Products' 

    service_order_line_id = fields.Many2one('service.order.line', ondelete='cascade')
    sale_line_id = fields.One2many('sale.order.line', 'service_order_line_product_id')
    invoice_line_ids = fields.One2many('account.move.line', 'service_order_line_product_id')
    qty_to_invoice = fields.Float(compute='_compute_qty_invoice', store=True, readonly=False)
    qty_invoiced = fields.Float(compute='_compute_qty_invoice', store=True, readonly=False)
    product_id = fields.Many2one('product.product')
    quantity = fields.Integer()
    unit_price = fields.Float()

    def _compute_display_name(self):
        super()._compute_display_name()
        for record in self:
            record.display_name = f"{record.product_id.name}"

    @api.depends('quantity',  'invoice_line_ids.quantity',  'invoice_line_ids.move_id.state')
    def _compute_qty_invoice(self):
        for record in self:
            qty_invoiced = sum( record.invoice_line_ids.filtered(lambda x: x.move_id.state != 'cancel').mapped('quantity'))
            record.qty_invoiced = qty_invoiced
            record.qty_to_invoice = record.quantity - qty_invoiced

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            record.unit_price = record.product_id.list_price
    
    def write(self, vals):
        if 'service_order_line_id' in vals and not vals['service_order_line_id']:
            self.unlink()
            return True
        return super().write(vals)