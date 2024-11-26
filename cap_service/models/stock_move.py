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