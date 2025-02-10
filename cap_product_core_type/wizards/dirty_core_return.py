# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID, Command
from odoo.exceptions import ValidationError


class dirtyCoreReturn(models.TransientModel):
    _name = 'dirty_core.return'


    model = fields.Selection(selection=[('sale.order', 'Sale'),('purchase.order', 'Purchase')], string="Model")
    partner_id = fields.Many2one('res.partner')
    core_return_id = fields.Many2one('core.return')
    ticket_id = fields.Many2one('helpdesk.ticket')
    lines = fields.One2many('dirty_core.return.line', 'core_return_id', string="Lines")
    suitable_product_ids = fields.Many2many('product.product')
    suitable_product_ids_domain = fields.Char("products domain", compute="_compute_suitable_product_ids_domain")
    put_in_batch = fields.Boolean(string="Put In Batch", default=False)

    @api.onchange('partner_id')
    def on_change_partner_id(self):
        if self.lines:
            self.lines.unlink()


    @api.depends('partner_id','model')
    def _compute_suitable_product_ids_domain(self):
        domain = [('is_core_type','=', True)]
        if self.partner_id:
            suitable_order_lines = self.env[self.model].search([('state','in',['sale','purchase','done']),('partner_id','=', self.partner_id.id)])
            filtered_product_ids = suitable_order_lines.order_line.filtered(lambda l:l.product_id.is_core_type and l.is_core_part).mapped('product_id.id')

            if filtered_product_ids:
                domain += [('id', 'in', filtered_product_ids)]
            else:
                domain = [('id','in',[])]

        self.suitable_product_ids_domain = domain

    def action_confirm(self):
        for rec in self:
            if rec.model == 'purchase.order':
                pickings = rec.create_purchase_return()
                return pickings
            else:
                pickings = rec.sales_return()
                return pickings

    def sales_return(self):
        # we only need to assign a total of moves that have same quantities as we are returning
        moves = self.select_moves_for_return(self.lines)

        try:
            moves._action_assign()
        except:
            # incase moves already assigned
            pass
        new_picking_ids = moves.mapped('picking_id')
        if self.put_in_batch:
            # if we have multiple picking batch them
            self.env['stock.picking.to.batch'].with_context({'active_ids': new_picking_ids.ids}).create({
                'mode': 'new',
                'is_create_draft': True,
            }).attach_pickings()
            if new_picking_ids.batch_id:
                new_picking_ids.batch_id.action_confirm()
        if self.ticket_id:
            # link to helpdesk ticket
            self.ticket_id.picking_ids |= new_picking_ids
            new_picking_ids.message_post_with_source(
                'helpdesk.ticket_creation',
                render_values={'self': new_picking_ids, 'ticket': self.ticket_id},
                subtype_xmlid='mail.mt_note',
            )
        return {
            'name': _('Returned Picking'),
            'view_mode': 'tree,form,calendar',
            'res_model': 'stock.picking',
            'domain': [('id', 'in', new_picking_ids.ids)],
            'type': 'ir.actions.act_window',
        }

    def select_moves_for_return(self,lines):
        selected_moves = self.env['stock.move']
        for line in lines:
            moves = line.original_moves.filtered(lambda m: m.state not in ['draft','cancel','done'])
            return_qty = line.quantity
            moves.sorted(lambda m:m.quantity)
            total = 0

            for move in moves:
                if total + move.quantity <= return_qty:
                    selected_moves += move
                    total += move.quantity
                if total == return_qty:
                    break  # Stop once we reach the required quantity
            if total == return_qty:
                break

        return selected_moves


    def create_purchase_return(self):
        procurements = []
        for line in self.lines:
            for move in line.po_lines :
                values = {
                    'group_id': move.order_id.group_id,
                    'route_ids': self.env['stock.route'].search([('company_id','=',self.env.company.id), ('name','like','(pick + pack + ship)')]),
                    'warehouse_id': self.env['stock.warehouse'].search([('company_id','=',self.env.company.id)]) or False,
                    'partner_id': self.partner_id.id,
                    'product_description_variants': line.product_id.name,
                    'company_id': self.env.company,
                    'purchase_line_id': move.id,
                }
                product_qty = move.product_qty
                line_uom = line.product_id.uom_id
                procurements.append(line._create_procurement(product_qty, line_uom, values))
        if procurements:
            self.env['procurement.group'].sudo().run(procurements)

        new_picking_ids = self.env['stock.picking'].search([('origin','=', self.core_return_id.name)])
        if new_picking_ids:
            if self.core_return_id:
                # link to helpdesk ticket
                self.core_return_id.picking_ids |= new_picking_ids
            result = self.env["ir.actions.actions"]._for_xml_id('stock.action_picking_tree_all')
            result['domain'] = [('id', 'in', new_picking_ids.ids)]

            return result
        else:
            return False


class dirtyCoreReturnLine(models.TransientModel):
    _name = 'dirty_core.return.line'

    core_return_id = fields.Many2one('dirty_core.return')
    product_id = fields.Many2one('product.product', string="Product")
    suitable_product_ids_domain = fields.Char(related="core_return_id.suitable_product_ids_domain")
    original_moves = fields.Many2many('stock.move')
    po_lines = fields.Many2many('purchase.order.line')
    quantity = fields.Float("Return Quantity")
    allowed_quantity = fields.Float("Allowed Quantity")

    @api.onchange('product_id')
    def _compute_quantity_allowed(self):
        for line in self:
            line.allowed_quantity = 0
            if line.product_id:
                suitable_order_lines = self.env[self.core_return_id.model].search([('state','in',['sale','purchase','done']),('partner_id', '=', self.core_return_id.partner_id.id)]).order_line
                filtered_product_qty = suitable_order_lines.filtered(
                    lambda l: l.product_id.is_core_type and l.is_core_part and l.product_id == line.product_id).mapped('qty_delivered' if self.core_return_id.model == 'sale.order' else 'qty_received')
                line.allowed_quantity = sum(filtered_product_qty) or 0
                line.compute_original_moves(lines=suitable_order_lines)

    @api.onchange('quantity')
    def _check_quantity_allowed(self):
        if self.quantity != 0 and self.quantity > self.allowed_quantity:
            raise ValidationError (f" Quantity Allowed is {self.allowed_quantity}")
        self._compute_quantity_allowed()

    def compute_original_moves(self, lines=False):
        if lines:
            if self.core_return_id.model == 'sale.order':
                lines = lines.filtered(
                    lambda l: l.product_id.is_core_type and l.is_core_part and l.product_id == self.product_id).move_ids.filtered(lambda m:m.picking_code == 'incoming' and m.state not in ['draft','cancel','done']).ids
            elif self.core_return_id.model == 'purchase.order':
                moves = lines.filtered(
                    lambda l: l.product_id.is_core_type and l.is_core_part and l.product_id == self.product_id)
                self.po_lines = self.get_po_lines(moves)
                lines = False
            self.original_moves = lines

    def get_po_lines(self,lines):
        for line in self:
            required_qty = line.quantity  # Target quantity
            po_lines = []
            total_qty = 0

            for po in lines:
                if total_qty < required_qty:
                    po_lines.append(po)
                    total_qty += po.product_qty
                if total_qty >= required_qty:
                    break  # Stop once we reach the required quantity

            return lines.filtered(lambda l: l in po_lines)

    def _create_procurement(self, product_qty, procurement_uom, values):
        self.ensure_one()
        return self.env['procurement.group'].Procurement(
            self.product_id, product_qty, procurement_uom, self.core_return_id.partner_id.property_stock_customer,
            self.product_id.display_name, self.core_return_id.core_return_id.name, self.env.company, values)

