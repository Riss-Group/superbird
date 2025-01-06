from odoo import models, fields, api
from odoo.exceptions import UserError


class ServiceRentalOrder(models.TransientModel):
    _name = 'fleet.ack'
    _description = 'Fleet Acknowledgement'


    fleet_vehicle_ids = fields.Many2many('fleet.vehicle')
    ack_file = fields.Binary(string="Acknowledgement PDF")
    

    def button_save(self):
        self.fleet_vehicle_ids.ack_file = self.ack_file
        self.fleet_vehicle_ids._create_fleet_pdi(direction='in')
        return True
