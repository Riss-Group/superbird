
from odoo import api, fields, models
from odoo.fields import Command


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
    invoice_count = fields.Integer(string="Invoice Count", compute='_get_invoiced')
    invoice_ids = fields.Many2many(
        comodel_name='account.move',
        string="Invoices",
        compute='_get_invoiced',
        search='_search_invoice_ids',
        copy=False)
    return_count = fields.Integer(string="Return Count", compute='_get_returned')


    def _get_returned(self):
        for rec in self:
            picking_ids = self.env['stock.picking'].search([('warranty_claim_id', '=', rec.id)])
            rec.return_count = len(picking_ids.ids)

    def action_view_return(self):
        return self._get_action_view_picking()

    def _get_action_view_picking(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
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
        # The invoice_ids are obtained thanks to the invoice lines of the SO
        # lines, and we also search for possible refunds created directly from
        # existing invoices. This is necessary since such a refund is not
        # directly linked to the SO.
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
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()

        values = {
            # 'ref': self.client_order_ref or '',
            'move_type': 'out_invoice',
            # 'narration': self.note,
            # 'currency_id': self.currency_id.id,
            # 'medium_id': self.medium_id.id,
            # 'source_id': self.source_id.id,
            # 'team_id': self.team_id.id,
            'partner_id': self.partner_id.id,
            'partner_shipping_id': self.partner_id.id,
            'fiscal_position_id': self.env['account.fiscal.position']._get_fiscal_position(self.partner_id).id, #partner_invoice_id
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.partner_id.with_company(self.company_id).property_payment_term_id.id,
            # 'invoice_user_id': self.user_id.id,
            # 'payment_reference': self.reference,
            # 'transaction_ids': [Command.set(self.transaction_ids.ids)],
            'company_id': self.company_id.id,
            'invoice_line_ids': [],
            # 'user_id': self.user_id.id,
        }
        # if self.journal_id:
        #     values['journal_id'] = self.journal_id.id
        return values

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
        # if len(self) == 1:
        #     context.update({
        #         'default_partner_id': self.partner_id.id,
        #         'default_partner_shipping_id': self.partner_shipping_id.id,
        #         'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or
        #                                            self.env['account.move'].default_get(
        #                                                ['invoice_payment_term_id']).get('invoice_payment_term_id'),
        #         'default_invoice_origin': self.name,
        #     })
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
            'return_lines': [Command.create(line._prepare_return_line()) for line in self.warranty_claim_line_ids],
        })
        return warranty_return_id

    def action_create_vendor_return(self):
        picking_type_id = self.env['stock.picking.type'].search([('sequence_code', '=', 'RMA/OUT'),
                                                                 ('company_id', '=', self.company_id.id)], limit=1)
        warranty_return_id = self.create_return('to_supplier', picking_type_id)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'warranty.claim.return',
            'view_mode': 'form',
            'target': 'new',
            'res_id': warranty_return_id.id,
            # 'context': {
            #     'default_claim_id': self.id
            # }
        }

    def action_create_customer_return(self):
        picking_type_id = self.env['stock.picking.type'].search([('sequence_code', '=', 'RMA/IN'),
                                                                 ('company_id', '=', self.company_id.id)], limit=1)
        warranty_return_id = self.create_return('from_customer', picking_type_id)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'warranty.claim.return',
            'view_mode': 'form',
            'target': 'new',
            'res_id': warranty_return_id.id,
            # 'context': {
            #     'default_claim_id': self.id
            # }
        }

class WarrantyClaimLine(models.Model):
    _name = 'warranty.claim.line'
    _description = "Warranty claim Line"

    warranty_claim_id = fields.Many2one('warranty.claim', string="Warranty claim")
    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Integer(string="Quantity")
    unit_price = fields.Float(string="Unit Price")
    claim_for = fields.Selection([('product', 'Product'),('labor', 'Labor')])
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)
    service_order_line_id = fields.Many2one('service.order.line', string="Service order line")
    invoice_lines = fields.Many2many('account.move.line',
                                     relation='warranty_claim_line_invoice_rel',
                                     column1='warranty_claim_line_id', column2='invoice_line_id',
                                     string='Invoice Lines', copy=False)

    @api.depends('unit_price', 'quantity')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.quantity * record.unit_price

    def _prepare_invoice_line(self):
        """Prepare the values to create the new invoice line for a sales order line.

        :param optional_values: any parameter that should be added to the returned invoice line
        :rtype: dict
        """
        self.ensure_one()
        res = {
            'display_type': 'product',
            # 'sequence': self.sequence,
            'name': self.product_id.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_id.uom_id.id,
            'quantity': self.quantity,
            # 'discount': self.discount,
            'price_unit': self.unit_price,
            # 'tax_ids': [Command.set(self.tax_id.ids)],
            'warranty_claim_line_ids': [Command.link(self.id)],
            # 'is_downpayment': self.is_downpayment,
        }
        # self._set_analytic_distribution(res)
        return res

    # def _set_analytic_distribution(self, inv_line_vals):
    #     analytic_account_id = self.order_id.analytic_account_id.id
    #     if self.analytic_distribution:
    #         inv_line_vals['analytic_distribution'] = self.analytic_distribution
    #     if analytic_account_id and not self.display_type:
    #         analytic_account_id = str(analytic_account_id)
    #         if 'analytic_distribution' in inv_line_vals:
    #             inv_line_vals['analytic_distribution'][analytic_account_id] = inv_line_vals[
    #                                                                               'analytic_distribution'].get(
    #                 analytic_account_id, 0) + 100
    #         else:
    #             inv_line_vals['analytic_distribution'] = {analytic_account_id: 100}

    def _prepare_return_line(self):
        return {
            'product_id': self.product_id.id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'warranty_claim_line_id': self.id,
        }