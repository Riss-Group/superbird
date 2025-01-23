# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class StockReturnPickingLines(models.TransientModel):
    _name = 'stock.return.picking.lines'
    _rec_name = 'product_id'
    _description = 'Return Picking Line'

    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Float("Quantity", digits='Product Unit of Measure', required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id')
    wizard_id = fields.Many2one('stock.return.picking', string="Wizard")
    move_id = fields.Many2one('stock.move', "Move")
    picking_id = fields.Many2one('stock.picking', "Picking", domain="[('picking_type_id.code', '=', 'outgoing')]", compute="_compute_picking") # need to add picking dynamic domain
    sale_id = fields.Many2one('sale.order', "Sale")
    sale_domain = fields.Char("Sale domain", compute="_compute_sale_domain")
    suitable_product_ids_domain = fields.Char("products domain", compute="_compute_suitable_product_ids_domain")
    to_refund = fields.Boolean(string="Update quantities on SO/PO", default=True,
        help='Trigger a decrease of the delivered/received quantity in the associated Sale Order/Purchase Order')
    return_reason = fields.Many2one('stock.return.reason', string="Return Reason")

    @api.onchange('sale_id','move_id')
    def _check_sale_order(self):
        for rec in self:
            move = rec.move_id
            if move:
                # check if there is already a ready / waiting RMA return for the same Sale and Product
                existing_rma_return =move.sale_line_id.move_ids.filtered(
                    lambda m:m.picking_id.picking_type_id == rec.wizard_id.default_operation_type and m.state not in ('draft','done','cancel'))
                if existing_rma_return:
                    return {
                        'warning': {
                            'title': _('RMA Return Already Exists'),
                            'message': _(
                                f"There is already an RMA Return for the Product {rec.product_id.name} "
                                f"and Sale {rec.sale_id.name}.\n\n"
                                f"Please check the following jobs : {existing_rma_return.mapped('picking_id.name')} before confirming."
                            ),
                        }
                    }

    @api.onchange('product_id')
    def _compute_sale_order(self):
        for rec in self:
            # Filter suitable sale orders based on the product ID
            suitable_sale_order = next(
                (s for s in rec.wizard_id.suitable_sale_order_ids.order_line.filtered(lambda l: l.product_id == rec.product_id and l.qty_delivered > 0)
                 if s.move_ids.filtered(lambda m: m.picking_code == 'outgoing' and m.state == 'done') and
                 s.order_id not in rec.wizard_id.product_return_move_lines.mapped('sale_id')
                 ),
                None
            )
            if suitable_sale_order:
                rec.sale_id = suitable_sale_order.order_id
                rec._compute_picking()
            else:
                rec.sale_id = False
                rec.picking_id = False

    @api.onchange('quantity')
    def _check_quantity_allowed_to_return(self):
        for rec in self:
            allowed_qty = rec.move_id.sale_line_id.qty_delivered if rec.move_id.sale_line_id else rec.move_id.quantity
            if rec.quantity and rec.quantity > allowed_qty:
                rec.quantity = 0
                return {
                    'warning': {
                        'title': _(f'Quantity Allowed is {allowed_qty}'),
                        'message': _("You can't returned more than you have delivered."),
                    }
                }

    @api.depends('product_id','sale_id')
    def _compute_picking(self):
        for rec in self:
            if rec.sale_id:
                # Filter the picking related to the sale order
                outgoing_picking = next(
                    (move.picking_id for move in rec.sale_id.order_line.move_ids
                     if move.picking_code == 'outgoing' and move.state == 'done'),
                    None
                )
                if outgoing_picking:
                    move = next(
                        (m for m in outgoing_picking.move_ids_without_package
                         if m.product_id == rec.product_id),
                        None
                    )
                    if move :
                        data = ({
                            'picking_id': outgoing_picking.id,
                            'move_id': move.id,
                        })
                        if not rec.quantity:
                            data.update({
                                'quantity': 0,
                            })
                        rec.update(data)
                        continue
            # Default values if no conditions are met
            rec.update({'picking_id': False, 'move_id': False, 'quantity': 0})

    @api.depends('product_id','wizard_id.suitable_sale_order_ids','wizard_id.suitable_product_ids')
    def _compute_suitable_product_ids_domain(self):
        domain = []
        if self.wizard_id.suitable_sale_order_ids:
            suitable_sale_order_lines = self.wizard_id.suitable_sale_order_ids.order_line.filtered(
                lambda line: line.qty_delivered > 0)
            filtered_product_ids = suitable_sale_order_lines.mapped('product_id.id')

            if filtered_product_ids:
                domain += [('id', 'in', filtered_product_ids)]
        if self.wizard_id.suitable_product_ids:
            domain += [('id', 'in', self.wizard_id.suitable_product_ids.ids)]

        self.suitable_product_ids_domain = domain

    @api.depends('product_id','sale_id','wizard_id.suitable_sale_order_ids','wizard_id.product_return_move_lines')
    def _compute_sale_domain(self):
        domain = []
        if self.wizard_id.suitable_sale_order_ids:
            suitable_sale_order = self.wizard_id.suitable_sale_order_ids
            domain += [('id', 'in', suitable_sale_order.ids)]
        if self.product_id:
            sale_order_ids = self.wizard_id.suitable_sale_order_ids.order_line.filtered(
                lambda line: line.qty_delivered > 0 and line.product_id == self.product_id).mapped('order_id.id')
            domain += [('id', 'in', sale_order_ids)]
        if self.wizard_id.product_return_move_lines:
            domain += [('id', 'not in', self.wizard_id.product_return_move_lines.mapped('sale_id.id'))]

        self.sale_domain = domain



class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'


    @api.model
    def default_get(self, fields):
        res = super(StockReturnPicking, self).default_get(fields)
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'helpdesk.ticket':
            ticket = self.env['helpdesk.ticket'].browse(self.env.context.get('active_id'))
            if ticket.exists() and ticket.team_id and ticket.team_id.default_return_operation_type:
                res.update({'default_operation_type': ticket.team_id.default_return_operation_type.id})
        return res


    suitable_product_ids = fields.Many2many('product.product')
    suitable_product_ids_domain = fields.Char("products domain", compute="_compute_suitable_product_ids_domain")
    product_return_move_lines = fields.One2many('stock.return.picking.lines', 'wizard_id', 'Moves', readonly=False, store=True)
    default_operation_type = fields.Many2one('stock.picking.type', domain="[('code','=', 'incoming')]")

    @api.depends('suitable_picking_ids','suitable_sale_order_ids')
    def _compute_suitable_product_ids_domain(self):
        domain = []
        if self.suitable_sale_order_ids:
            suitable_sale_order_lines = self.suitable_sale_order_ids.mapped('order_line').filtered(
                lambda line: line.qty_delivered > 0)
            filtered_product_ids = suitable_sale_order_lines.mapped('product_id.id')

            if filtered_product_ids:
                domain += [('id', 'in', filtered_product_ids)]
        self.suitable_product_ids_domain = domain

    @api.depends('picking_id', 'suitable_product_ids')
    def _compute_moves_locations(self):
        super(StockReturnPicking, self)._compute_moves_locations()
        for wizard in self:
            suitable_product_ids = wizard.suitable_product_ids.ids
            moves_to_unlink = self.env['stock.return.picking.line']

            if suitable_product_ids:
                for move in wizard.product_return_moves:
                    if move.product_id.id not in suitable_product_ids:
                        moves_to_unlink |= move

                sale_orders = wizard.suitable_sale_order_ids.filtered(
                    lambda order: any(line.product_id.id in suitable_product_ids for line in order.order_line)
                )

                if wizard.sale_order_id.id in sale_orders.ids:
                    wizard.update({
                        'product_return_moves': [(3, move.id, False) for move in moves_to_unlink],
                    })
                else:
                    picking = sale_orders[-1].picking_ids
                    wizard.update({
                        'sale_order_id': sale_orders[-1].id,
                        'picking_id': picking[0].id,
                    })
                    wizard._compute_moves_locations()

    def _prepare_picking_default_values(self):
        vals = super(StockReturnPicking, self)._prepare_picking_default_values()
        if self.ticket_id and self.default_operation_type:
            vals.update({
                'picking_type_id': self.default_operation_type.id,
                'location_id': self.default_operation_type.default_location_src_id.id,
                'location_dest_id': self.default_operation_type.default_location_dest_id.id,
                'return_id': self.picking_id.id,
            })
        return vals

    def _create_picking_returns(self):
        for return_move in self.product_return_move_lines.mapped('move_id'):
            return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()

        #group by picking_ids in product_return_move_lines
        new_picking_ids = self.env["stock.picking"]
        for picking in self.product_return_move_lines.mapped('move_id.picking_id') :
            # create new picking for returned products
            new_picking = picking.copy(self._prepare_picking_default_values())
            picking_type_id = new_picking.picking_type_id.id
            new_picking.message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': new_picking, 'origin': picking},
                subtype_xmlid='mail.mt_note',
            )
            new_picking_ids += new_picking
            returned_lines = 0
            for return_line in self.product_return_move_lines.filtered(lambda m: m.move_id.picking_id == picking):
                if not return_line.move_id:
                    raise UserError(_("You have manually created product lines, please delete them to proceed."))
                if not float_is_zero(return_line.quantity, precision_rounding=return_line.uom_id.rounding):
                    returned_lines += 1
                    vals = self._prepare_move_default_values(return_line, new_picking)
                    r = return_line.move_id.copy(vals)
                    vals = {}

                    # +--------------------------------------------------------------------------------------------------------+
                    # |       picking_pick     <--Move Orig--    picking_pack     --Move Dest-->   picking_ship
                    # |              | returned_move_ids              ↑                                  | returned_move_ids
                    # |              ↓                                | return_line.move_id              ↓
                    # |       return pick(Add as dest)          return toLink                    return ship(Add as orig)
                    # +--------------------------------------------------------------------------------------------------------+
                    move_orig_to_link = return_line.move_id.move_dest_ids.mapped('returned_move_ids')
                    # link to original move
                    move_orig_to_link |= return_line.move_id
                    # link to siblings of original move, if any
                    move_orig_to_link |= return_line.move_id\
                        .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel'))\
                        .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel'))
                    move_dest_to_link = return_line.move_id.move_orig_ids.mapped('returned_move_ids')
                    # link to children of originally returned moves, if any. Note that the use of
                    # 'return_line.move_id.move_orig_ids.returned_move_ids.move_orig_ids.move_dest_ids'
                    # instead of 'return_line.move_id.move_orig_ids.move_dest_ids' prevents linking a
                    # return directly to the destination moves of its parents. However, the return of
                    # the return will be linked to the destination moves.
                    move_dest_to_link |= return_line.move_id.move_orig_ids.mapped('returned_move_ids')\
                        .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel'))\
                        .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel'))
                    vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link]
                    vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
                    r.write(vals)
            if not returned_lines:
                raise UserError(_("Please specify at least one non-zero quantity."))

        new_picking_ids.action_confirm()
        new_picking_ids.action_assign()
        return new_picking_ids, picking_type_id

    def create_picking_returns(self):
        for wizard in self:
            new_picking_ids, pick_type_id = wizard._create_picking_returns()
        # Override the context to disable all the potential filters that could have been set previously
        ctx = dict(self.env.context)
        ctx.update({
            'default_partner_id': self.ticket_id.partner_id.id,
            'search_default_picking_type_id': pick_type_id,
            'search_default_draft': False,
            'search_default_assigned': False,
            'search_default_confirmed': False,
            'search_default_ready': False,
            'search_default_planning_issues': False,
            'search_default_available': False,
            'create': False,
        })
        picking_ids = self.env['stock.picking'].browse(new_picking_ids.ids)
        ticket_id = self.ticket_id
        if ticket_id:
            ticket_id.picking_ids |= new_picking_ids
            new_picking_ids.message_post_with_source(
                'helpdesk.ticket_creation',
                render_values={'self': new_picking_ids, 'ticket': ticket_id},
                subtype_xmlid='mail.mt_note',
            )
        return {
            'name': _('Returned Picking'),
            'view_mode': 'tree,form,calendar',
            'res_model': 'stock.picking',
            'domain': [('id', 'in', new_picking_ids.ids)],
            'type': 'ir.actions.act_window',
            'context': ctx,
        }