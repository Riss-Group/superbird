# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    suitable_product_ids = fields.Many2many('product.product')
    suitable_product_ids_domain = fields.Char("products domain", compute="_compute_suitable_product_ids_domain")


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