from odoo import  models, fields, api, _
from odoo.exceptions import UserError
from odoo.osv import expression


class FleetVehicleWarrantyLine(models.Model):
    _inherit = 'fleet.vehicle'
    

    fleet_vehicle_warranty_line = fields.One2many('fleet.vehicle.warranty.line', 'fleet_vehicle_id')
    stock_number = fields.Char()
    body_number = fields.Char()
    customer_id = fields.Many2one('res.partner')

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if operator != 'ilike' or (name or '').strip():
            domain = ['|', ('name', 'ilike', name), '|', ('brand_id.name', 'ilike', name), '|', ('vin_sn', 'ilike', name), ('body_number', 'ilike', name) ]
        return self._search(domain, limit=limit, order=order)
