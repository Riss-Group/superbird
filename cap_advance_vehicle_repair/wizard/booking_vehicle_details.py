from odoo import fields, api, models, _


class BookingVehicleDetails(models.TransientModel):
    _inherit = 'booking.vehicle.details'


    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Fleet Vehicle")
    fleet_sold_date = fields.Date(related='fleet_vehicle_id.sold_date')
    fleet_warranty_period = fields.Integer(related='fleet_vehicle_id.warranty_period')
    fleet_warranty_expired = fields.Boolean(related='fleet_vehicle_id.warranty_expired')

    @api.model
    def default_get(self, field):
        res = super().default_get(field)
        res['vehicle_booking_id'] = self._context.get('active_id')
        res['customer_id'] = self._context.get('customer_id')
        res['vehicle_type'] = 'fleet_vehicle'
        return res

    def action_add_vehicle_details(self):
        res = super().action_add_vehicle_details()
        rec = self._context.get('active_id')
        vehicle_booking_id = self.env['vehicle.booking'].browse(rec)
        data = {
            'fleet_vehicle_id': self.fleet_vehicle_id,
        }
        vehicle_booking_id.write(data)
