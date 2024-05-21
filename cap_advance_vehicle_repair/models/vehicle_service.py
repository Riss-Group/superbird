from odoo import models, fields, api


class VehicleService(models.Model):
    _inherit = 'vehicle.service'

    vehicle_complaint_id = fields.Many2one('vehicle.ccc', string = 'Complaint', domain="[('ttype', '=', 'p')]")
    vehicle_cause_id = fields.Many2one('vehicle.ccc', string = 'Cause', domain="[('ttype', '=', 'c')]")
    vehicle_correction_id = fields.Many2one('vehicle.ccc', string = 'Correction', domain="[('ttype', '=', 'r')]")
    description = fields.Text()