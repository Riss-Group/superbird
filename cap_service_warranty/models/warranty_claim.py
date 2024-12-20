
from odoo import api, fields, models


class WarrantyClaim(models.Model):
    _name = 'warranty.claim'
    _description = "Warranty claim"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Name")
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('approved', 'Approved'),
                              ('refused', 'Refused'), ('in_payment', 'In Payment'), ('paid', 'Paid')], default="draft")
    partner_id = fields.Many2one('res.partner', string="Contact")
    warranty_claim_line_ids = fields.One2many('warranty.claim.line', 'warranty_claim_id', string="Warranty claim Line")
    service_order_id = fields.Many2one('service.order', string="Service Order")
    order_total = fields.Float(string="Order Total", compute="_compute_order_total", store=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    ticket_number = fields.Char(string="Ticket Number")

    @api.depends('warranty_claim_line_ids', 'warranty_claim_line_ids.subtotal')
    def _compute_order_total(self):
        for record in self:
            record.order_total = sum(record.mapped('warranty_claim_line_ids.subtotal'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name', ''):
                vals['name'] = self.env['ir.sequence'].next_by_code('warranty.claim')
        return super().create(vals_list)

    def action_create_invoice(self):
        return True

    def action_stat_button_invoice_ids(self):
        return True


class WarrantyClaimLine(models.Model):
    _name = 'warranty.claim.line'
    _description = "Warranty claim Line"

    warranty_claim_id = fields.Many2one('warranty.claim', string="Warranty claim")
    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Integer(string="Quantity")
    unit_price = fields.Float(string="Unit Price")
    claim_for = fields.Selection([('product', 'Product'),('labor', 'Labor')])
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)

    @api.depends('unit_price', 'quantity')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.quantity * record.unit_price
