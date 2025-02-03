# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.fields import Command
from odoo.exceptions import UserError


class WarrantyClaim(models.Model):
    _name = 'warranty.claim'
    _description = "Warranty claim"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Name")
    state = fields.Selection(selection=[('draft', 'Draft'), ('confirmed', 'Confirmed'), ('approved', 'Approved'),
                                        ('refused', 'Refused'), ('in_payment', 'In Payment'), ('paid', 'Paid'),
                                        ('cancel', 'Cancel')], default="draft")
    partner_id = fields.Many2one('res.partner', string="Contact")
    warranty_claim_line_ids = fields.One2many('warranty.claim.line', 'warranty_claim_id', string="Warranty claim Line")
    service_order_id = fields.Many2one('service.order', string="Service Order")
    order_total = fields.Float(string="Order Total", compute="_compute_order_total", store=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    ticket_number = fields.Char(string="Claim Number")
    invoice_count = fields.Integer(string="Invoice Count", compute='_get_invoiced')
    invoice_ids = fields.Many2many(comodel_name='account.move', string="Invoices", compute='_get_invoiced',
                                   search='_search_invoice_ids', copy=False)
    return_count = fields.Integer(string="Return Count", compute='_get_returned')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True,
                                   compute='_compute_warehouse_id', store=True, readonly=False, precompute=True,
                                   check_company=True)
    service_order_line_ids = fields.Many2many('service.order.line',  compute='_compute_service_order_line', store=True,
                                              readonly=False, string="Service order line")

    def _compute_service_order_line(self):
        for rec in self:
            rec.service_order_line_ids = rec.warranty_claim_line_ids.mapped('service_order_line_id')

    @api.depends('company_id')
    def _compute_warehouse_id(self):
        for order in self:
            warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', order.company_id.id)], limit=1)
            order.warehouse_id = warehouse_id.id

    def _get_returned(self):
        for rec in self:
            picking_ids = self.env['stock.picking'].search([('warranty_claim_id', '=', rec.id)])
            rec.return_count = len(picking_ids.ids)

    def action_view_return(self):
        return self._get_action_view_picking()

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def _get_action_view_picking(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        pickings =self.env['stock.picking'].search([('warranty_claim_id', '=', self.id)])
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        # Prepare the context.
        picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
        if picking_id:
            picking_id = picking_id[0]
        else:
            picking_id = pickings[0]
        # View context from sale_renting `rental_schedule_view_form`
        cleaned_context = {k: v for k, v in self._context.items() if k != 'form_view_ref'}
        action['context'] = dict(cleaned_context, default_partner_id=self.partner_id.id,
                                 default_picking_type_id=picking_id.picking_type_id.id, default_origin=self.name,
                                 default_group_id=picking_id.group_id.id)
        return action

    @api.depends('warranty_claim_line_ids.invoice_lines')
    def _get_invoiced(self):
        for order in self:
            invoices = order.warranty_claim_line_ids.invoice_lines.move_id.filtered(
                lambda r: r.move_type in ('out_invoice'))
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)

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
        for rec in self:
            invoice = self.env['account.move'].sudo().create(
                rec._prepare_invoice_values(rec, rec.warranty_claim_line_ids)
            )
            rec.state = 'in_payment'
        return True

    def _prepare_invoice_values(self, order, wc_lines):
        self.ensure_one()
        return {
            **order._prepare_invoice(),
            'invoice_line_ids': [Command.create(line._prepare_invoice_line()) for line in wc_lines],
        }

    def _prepare_invoice(self):
        self.ensure_one()
        return {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'partner_shipping_id': self.partner_id.id,
            'fiscal_position_id': self.env['account.fiscal.position']._get_fiscal_position(self.partner_id).id, #partner_invoice_id
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.partner_id.with_company(self.company_id).property_payment_term_id.id,
            'company_id': self.company_id.id,
            'invoice_line_ids': [],
        }

    def action_view_invoice(self, invoices=False):
        if not invoices:
            invoices = self.mapped('invoice_ids')
        action = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        action['context'] = context
        return action

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_refuse(self):
        self.write({'state': 'refused'})

    def create_return(self, is_return, picking_type_id=False):
        warranty_return_id = self.env['warranty.claim.return'].create({
            'warranty_claim_id': self.id,
            'is_return': is_return,
            'picking_type_id': picking_type_id.id if picking_type_id else False,
            'partner_id': self.partner_id.id,
            'return_lines': [Command.create(line._prepare_return_line())
                             for line in self.warranty_claim_line_ids.filtered(lambda l: not l.display_type and l.claim_for == 'product')],
        })
        return warranty_return_id

    def action_create_vendor_return(self):
        if not self.warehouse_id.rma_out_type_id:
            raise UserError(_("Please set RMA Out for warehouse %s") % self.warehouse_id.name)
        warranty_return_id = self.create_return('to_supplier', self.warehouse_id.rma_out_type_id)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'warranty.claim.return',
            'view_mode': 'form',
            'target': 'new',
            'res_id': warranty_return_id.id,
        }

    def action_create_customer_return(self):
        if not self.warehouse_id.rma_in_type_id:
            raise UserError(_("Please set RMA In for warehouse %s") % self.warehouse_id.name)
        warranty_return_id = self.create_return('from_customer', self.warehouse_id.rma_in_type_id)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'warranty.claim.return',
            'view_mode': 'form',
            'target': 'new',
            'res_id': warranty_return_id.id,
        }

    def action_view_job_line(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Job Line',
            'view_mode': 'tree',
            'view_id': self.env.ref('cap_service_warranty.view_service_order_line_tree_view_1').id,
            'res_model': 'service.order.line',
            'context': {
            },
            'domain': [('id', 'in', self.warranty_claim_line_ids.mapped('service_order_line_id').ids)]
        }

class WarrantyClaimLine(models.Model):
    _name = 'warranty.claim.line'
    _description = "Warranty claim Line"

    warranty_claim_id = fields.Many2one('warranty.claim', string="Warranty claim")
    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Integer(string="Quantity")
    unit_price = fields.Float(string="Unit Price")
    claim_for = fields.Selection(selection=[('product', 'Product'),('labor', 'Labor')], string="Claim For")
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)
    service_order_line_id = fields.Many2one('service.order.line', string="Service order line")
    invoice_lines = fields.Many2many('account.move.line', relation='warranty_claim_line_invoice_rel',
                                     column1='warranty_claim_line_id', column2='invoice_line_id',
                                     string='Invoice Lines', copy=False)
    name = fields.Text(string="Description", compute='_compute_name', store=True, readonly=False, required=True,
                       precompute=True)
    display_type = fields.Selection(selection=[('line_section', "Section"), ('line_note', "Note")], default=False)

    @api.depends('product_id')
    def _compute_name(self):
        for record in self:
            if record.product_id:
                record.name = record.product_id.get_product_multiline_description_sale()

    @api.depends('unit_price', 'quantity')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.quantity * record.unit_price

    def _prepare_invoice_line(self):
        self.ensure_one()
        res = {
            'display_type': 'product',
            'name': self.product_id.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_id.uom_id.id,
            'quantity': self.quantity,
            'price_unit': self.unit_price,
            'warranty_claim_line_ids': [Command.link(self.id)],
        }
        return res

    def _prepare_return_line(self):
        return {
            'product_id': self.product_id.id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'warranty_claim_line_id': self.id,
        }
