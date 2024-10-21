from odoo import  models, fields, api, _
from odoo.exceptions import UserError
from odoo.osv import expression


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    

    fleet_vehicle_warranty_line = fields.One2many('fleet.vehicle.warranty.line', 'fleet_vehicle_id')
    stock_number = fields.Char(tracking=True)
    body_number = fields.Char(tracking=True)
    customer_id = fields.Many2one('res.partner', ondelete="restrict", tracking=True)
    product_id = fields.Many2one('product.product', ondelete="restrict", tracking=True)
    sold_date = fields.Date(tracking=True)
    fleet_move_line_ids = fields.One2many('stock.move.line', 'fleet_vehicle_id')
    fleet_move_line_count = fields.Integer(compute='_compute_fleet_move_line_count')


    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if operator != 'ilike' or (name or '').strip():
            domain = ['|', ('name', 'ilike', name), '|', ('brand_id.name', 'ilike', name), '|', ('vin_sn', 'ilike', name), ('body_number', 'ilike', name) ]
        return self._search(domain, limit=limit, order=order)

    @api.depends('fleet_move_line_ids')
    def _compute_fleet_move_line_count(self):
        for record in self:
            record.fleet_move_line_count = len(record.fleet_move_line_ids)

    def action_fleet_move_lines(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fleet Moves',
            'view_mode': 'tree,form',
            'res_model': 'stock.move.line',
            'domain': [('id', 'in', self.fleet_move_line_ids.ids)]
        }
