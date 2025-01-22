from odoo import models, fields, api
from odoo.exceptions import UserError
from markupsafe import Markup


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    fleet_vehicle_ids = fields.Many2many('fleet.vehicle', compute='_compute_fleet_vehicle_ids')
    fleet_vehicle_count = fields.Integer(compute='_compute_fleet_vehicle_ids')
    show_service_ack = fields.Boolean(compute='_compute_show_service_ack')


    @api.depends('move_line_ids.fleet_vehicle_id')
    def _compute_fleet_vehicle_ids(self):
        for record in self:
            fleet_vehicle_ids = record.move_line_ids.fleet_vehicle_id
            record.fleet_vehicle_ids = fleet_vehicle_ids.ids
            record.fleet_vehicle_count = len(fleet_vehicle_ids)

    @api.depends('state', 'move_line_ids.service_ack', 'move_line_ids.fleet_vehicle_id')
    def _compute_show_service_ack(self):
        for picking in self:
            picking.show_service_ack = False
            if picking.picking_type_id.code != 'outgoing':
                continue
            if picking.state not in ('confirmed', 'waiting', 'assigned'):
                continue
            move_lines_with_fleet = picking.move_line_ids.filtered(lambda line: line.fleet_vehicle_id and line.product_id.create_pdi_delivery)
            if not move_lines_with_fleet:
                continue
            all_acknowledged = all(line.service_ack for line in move_lines_with_fleet)
            picking.show_service_ack = not all_acknowledged
    
    def action_ack_fleets(self):
        for picking in self:
            move_lines_with_fleet = picking.move_line_ids.filtered(lambda line: not line.service_ack and line.fleet_vehicle_id and line.product_id.create_pdi_delivery)
            move_lines_with_fleet.write({'service_ack': True})
            for line in move_lines_with_fleet:
                line._process_fleet_vehicle_out()
            if move_lines_with_fleet:
                stock_numbers = [line.fleet_vehicle_id.stock_number for line in move_lines_with_fleet if line.fleet_vehicle_id]
                stock_number_list_html = "".join(f"<li>{stock}</li>" for stock in stock_numbers)
                picking.message_post(
                    body=Markup(f"These fleet vehicles have been acknowledged:<br><ul>{stock_number_list_html}</ul>"),
                    subtype_xmlid='mail.mt_note'
                )

    def _action_done(self):
        for picking in self:
            if picking.picking_type_id.code == 'outgoing' and picking.state in ('confirmed', 'waiting', 'assigned'):
                move_lines_with_fleet = picking.move_line_ids.filtered(lambda line: line.fleet_vehicle_id and line.product_id.create_pdi_delivery)
                if move_lines_with_fleet and not all(line.service_ack for line in move_lines_with_fleet):
                    return {
                        'warning': {
                            'title': 'Unacknowledged Fleets',
                            'message': (
                                "Not all fleet vehicles have been acknowledged. "
                                "You are proceeding to validate the picking anyway."
                            ),
                        }
                    }
        return super()._action_done()
    
    def action_fleet_vehicle(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicles',
            'view_mode': 'kanban,tree,form',
            'res_model': 'fleet.vehicle',
            'domain': [('id', 'in', self.fleet_vehicle_ids.ids)]
        }

    def action_open_picking_form(self):
        """
        Action to open the current stock.picking record in form view.
        """
        return {
            'name': f"{self.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
            'views': [(self.env.ref('cap_service.view_picking_form_service_readonly').id, 'form')],
            'context': {
                'create': 0, 
                'edit':0,
                'delete':0,
            },
        }