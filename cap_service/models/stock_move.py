from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
logger = logging.getLogger()


class StockMove(models.Model):
    _inherit = 'stock.move'


    def _action_assign(self):
        super()._action_assign()
        for move_id in self:
            product_id = move_id.product_id
            if product_id.create_fleet_vehicle and move_id.picking_type_id.code == 'incoming' and product_id.sequence_code:
                next_number = product_id.sequence_id.number_next
                padding = product_id.sequence_id.padding
                next_serial_number = f"{product_id.sequence_prefix}{next_number:0{padding}d}"
                next_serial_count = len(move_id.move_line_ids.filtered(lambda l: not l.lot_name and not l.lot_id))
                move_id = move_id.with_context(self.env.context, use_sequence_serial=True)
                if next_serial_count > 0:
                    move_id._generate_serial_numbers(next_serial=next_serial_number,next_serial_count=next_serial_count)
            for move_line_id in move_id.move_line_ids:
                if product_id.create_fleet_vehicle and move_line_id.picking_type_id.code == 'incoming' and move_line_id.lot_name:
                    move_line_id._process_fleet_vehicle_in()

    def action_assign_serial(self):
        '''
            Opens a wizard to assign SN's name on each move lines.
            Override will add the option to auto generate a fleet serial number in the wizard logic
        '''
        action = super().action_assign_serial()
        action_context = action.get('context', {}).copy()
        action_context.update({
            'default_product_id': self.product_id.id,
            'default_move_id': self.id,
            'default_is_fleet_serial': self.product_id.create_fleet_vehicle,
        })
        action['context'] = action_context
        return action
    
    def _generate_serial_numbers(self, next_serial, next_serial_count=False, location_id=False):
        self.ensure_one()
        if self.env.context.get('use_sequence_serial') and self.product_id.create_fleet_vehicle and self.product_id.sequence_id:
            sequence_id = self.product_id.sequence_id
            lot_names = []
            for _ in range(next_serial_count or self.next_serial_count):
                next_serial_number = sequence_id.next_by_code(sequence_id.code)
                lot_names.append({'lot_name': next_serial_number, 'quantity': 1})
            move_lines_commands = self._generate_serial_move_line_commands(lot_names)
            self.move_line_ids = move_lines_commands
            return True
        else:
            return super()._generate_serial_numbers(next_serial, next_serial_count=next_serial_count, location_id=location_id)
    
    def _create_operation_quality_checks(self, pick_moves):
        """
            Override to include source and destination locations in the domain for quality checks.
        """
        check_vals_list = super()._create_operation_quality_checks(pick_moves)
        replacement_check_vals_list = []
        use_replacement = False
        for picking, moves in pick_moves.items():
            for move in moves:
                rental_location = picking.company_id.rental_loc_id
                dest_location = move.location_dest_id
                source_location = move.location_id
                if not rental_location or (source_location != rental_location and dest_location != rental_location):
                    continue
                use_replacement = True
                quality_points_domain = self.env['quality.point']._get_domain(
                    moves.product_id,
                    picking.picking_type_id,
                    measure_on='operation',
                    dest_location_id=dest_location if dest_location == rental_location else False,
                    source_location_id=source_location if source_location == rental_location else False
                )
                quality_points = self.env['quality.point'].sudo().search(quality_points_domain)
                for point in quality_points:
                    if point.check_execute_now():
                        replacement_check_vals_list.append({
                            'point_id': point.id,
                            'team_id': point.team_id.id,
                            'measure_on': 'operation',
                            'picking_id': picking.id,
                        })
        return replacement_check_vals_list if use_replacement else check_vals_list