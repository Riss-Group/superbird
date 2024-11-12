from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockAssignSerialNumbers(models.TransientModel):
    _inherit = 'stock.assign.serial'


    is_fleet_serial = fields.Boolean()
    predicted_serial = fields.Char()


    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        is_fleet_serial = self.env.context.get('default_is_fleet_serial', False)
        defaults['is_fleet_serial'] = is_fleet_serial
        if is_fleet_serial and defaults.get('product_id'):
            product_id = self.env['product.product'].browse(defaults.get('product_id'))
            if product_id.sequence_id:
                next_number = product_id.sequence_id.number_next
                padding = product_id.sequence_id.padding
                predicted_serial = f"{product_id.sequence_prefix}{next_number:0{padding}d}"
                defaults['next_serial_number'] = predicted_serial
                defaults['predicted_serial'] = predicted_serial
        return defaults
    
    def generate_serial_numbers(self):
        self.ensure_one()
        if self.is_fleet_serial and self.predicted_serial == self.next_serial_number:
            self = self.with_context(self.env.context, use_sequence_serial=True)
        res = super().generate_serial_numbers()
        return res