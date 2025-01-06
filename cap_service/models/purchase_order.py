from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    fleet_vehicle_ids = fields.Many2many('fleet.vehicle', compute='_compute_fleet_vehicle_data')
    fleet_vehicle_ids_count = fields.Integer(compute='_compute_fleet_vehicle_data')
    service_order_ids_count = fields.Integer(compute='_compute_fleet_vehicle_data')
    service_order_worksheet_count = fields.Integer(compute='_compute_fleet_vehicle_data')
    fleet_procurement_group_id = fields.Many2one('procurement.group', string='Fleet Procurement Group', copy=False,)

    
    @api.depends('picking_ids.move_line_ids')
    def _compute_fleet_vehicle_data(self):
        for record in self:
            fleet_vehicle_ids = record.picking_ids.move_line_ids.fleet_vehicle_id
            record.fleet_vehicle_ids = fleet_vehicle_ids
            record.fleet_vehicle_ids_count = len(fleet_vehicle_ids.ids)
            record.service_order_ids_count = sum(fleet_vehicle_ids.mapped('service_order_ids_count'))
            record.service_order_worksheet_count = sum(fleet_vehicle_ids.mapped('service_order_worksheet_count'))

    def action_service_order_ids(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Service Orders'),
            'view_mode': 'tree,form',
            'res_model': 'service.order',
            'domain': [('id', 'in', self.fleet_vehicle_ids.service_order_ids.ids)]
        }
    
    def action_view_worksheets(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Worksheets'),
            'view_mode': 'tree',
            'res_model': 'service.order.worksheets',
            'context': {'service_order_ids': self.fleet_vehicle_ids.service_order_ids.ids},
            'target': 'current',
        }
    
    def action_fleet_vehicle(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicles',
            'res_model': 'fleet.vehicle',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.fleet_vehicle_ids.ids)],
            'views': [
                (self.env.ref('cap_service.fleet_vehicle_view_tree_ack').id, 'tree'),
                (self.env.ref('fleet.fleet_vehicle_view_form').id, 'form'),
            ],
            'context': {
                'create': 0, 
                'delete':0,
            },
        }
    
    def _create_picking(self):
        for order in self.filtered(lambda po: po.state in ('purchase', 'done')):
            fleet_lines = order.order_line.filtered(lambda l: l.product_id.create_fleet_vehicle)
            non_fleet_lines = order.order_line - fleet_lines
            if non_fleet_lines:
                super(PurchaseOrder, order.with_context(skip_fleet_lines=True))._create_picking()
            if fleet_lines:
                fleet_lines._create_or_update_picking()

    def _prepare_fleet_picking(self, line):
        if not line:
            raise UserError(_("You must provide a line to create a picking for a fleet product."))
        if not self.fleet_procurement_group_id:
            self.fleet_procurement_group_id = self.env['procurement.group'].create({
                'name': f"{self.name} - Fleet Products",
                'move_type': 'direct',
                'partner_id': self.partner_id.id,
            })
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
            'state': 'draft',
        }
    
    def _prepare_picking(self):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s", self.partner_id.name))
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'user_id': False,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
            'state': 'draft',
        }


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _create_stock_moves(self, picking):
        order_id = self.mapped('order_id')
        if len(order_id) > 1:
            order_id = order_id[0]
        non_fleet_lines = self.filtered(lambda l: not l.product_id.create_fleet_vehicle)
        fleet_lines = self.filtered(lambda l: l.product_id.create_fleet_vehicle)
        standard_picking = picking
        if standard_picking and standard_picking.group_id and standard_picking.group_id == order_id.fleet_procurement_group_id:
            standard_picking = order_id.picking_ids.filtered(lambda p: 
                p.group_id != order_id.fleet_procurement_group_id and 
                p.state not in ('done', 'cancel') and 
                p.location_dest_id.usage in ('internal', 'transit', 'customer')
            )
            if not standard_picking and non_fleet_lines:
                standard_picking = self.env['stock.picking'].create(order_id._prepare_picking())
        if self.env.context.get('skip_fleet_lines'):
            return super(PurchaseOrderLine, non_fleet_lines)._create_stock_moves(standard_picking)
        res = super(PurchaseOrderLine, non_fleet_lines)._create_stock_moves(standard_picking)
        fleet_moves = self.env['stock.move']
        for line in fleet_lines:
            values = []
            for _ in range(int(line.product_qty)):
                move_vals = line._prepare_stock_move_vals(
                    picking,
                    price_unit=line._get_stock_move_price_unit(),
                    product_uom_qty=1,
                    product_uom=line.product_uom
                )
                values.append(move_vals)
            if values:
                fleet_moves += self.env['stock.move'].create(values)
        return res + fleet_moves

    def _create_or_update_picking(self):
        StockPicking = self.env['stock.picking']
        for line in self:
            is_fleet_product = line.product_id.create_fleet_vehicle
            if is_fleet_product:
                existing_qty = sum(line.move_ids.mapped('product_uom_qty'))
                qty_to_process = int(line.product_qty) - int(existing_qty)
                if qty_to_process > 0:
                    for _ in range(qty_to_process):
                        picking = StockPicking.create(line.order_id._prepare_fleet_picking(line=line))
                        move_vals = line._prepare_stock_move_vals(
                            picking,
                            price_unit=line._get_stock_move_price_unit(),
                            product_uom_qty=1,
                            product_uom=line.product_uom
                        )
                        move = self.env['stock.move'].create(move_vals)
                        move.write({'group_id': line.order_id.fleet_procurement_group_id.id})
                        move._action_confirm()._action_assign()
            else:
                super(PurchaseOrderLine, self)._create_or_update_picking()
