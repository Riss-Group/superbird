from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class VehicleBooking(models.Model):
    _inherit = 'vehicle.booking'

    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Fleet Vehicle")
    fleet_sold_date = fields.Date(related='fleet_vehicle_id.sold_date')
    fleet_warranty_period = fields.Integer(related='fleet_vehicle_id.warranty_period')
    fleet_warranty_expired = fields.Boolean(related='fleet_vehicle_id.warranty_expired')
    fleet_odometer_count = fields.Integer(related='fleet_vehicle_id.odometer_count')
    complaint_ids = fields.Many2many('vehicle.ccc', string='Customer complaints', domain = '[("ttype", "=", "p")]')
    vehicle_service_ids = fields.Many2many('vehicle.service', string="Services", domain="[('vehicle_complaint_id', 'in', complaint_ids)]")

    @api.constrains('vehicle_fuel_type_id')
    def _vehicle_fuels(self):
        for record in self:
            if not record.vehicle_fuel_type_id and record.vehicle_brand_id and record.vehicle_model_id:
                raise ValidationError("Please, add fuel type")

    @api.onchange('vehicle_service_ids', 'vehicle_spare_part_ids')
    def _onchange_vheicle_service_parts(self):
        self.estimate_cost = sum(self.vehicle_service_ids.mapped('service_charge')) + sum(self.vehicle_spare_part_ids.mapped('lst_price'))
    
    def action_view_odometer(self):
        return self.fleet_vehicle_id.with_context({'xml_id': 'fleet_vehicle_odometer_action' }).return_action_to_open()