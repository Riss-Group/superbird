from odoo import models, fields, api
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    fleet_vehicle_ids = fields.Many2many('fleet.vehicle', compute='_compute_fleet_vehicle_ids')
    fleet_vehicle_count = fields.Integer(compute='_compute_fleet_vehicle_ids')


    @api.depends('move_line_ids')
    def _compute_fleet_vehicle_ids(self):
        for record in self:
            fleet_vehicle_ids = record.move_line_ids.fleet_vehicle_id
            record.fleet_vehicle_ids = fleet_vehicle_ids.ids
            record.fleet_vehicle_count = len(fleet_vehicle_ids)
    
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