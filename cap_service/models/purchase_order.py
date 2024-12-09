from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    fleet_vehicle_ids = fields.Many2many('fleet.vehicle', compute='_compute_fleet_vehicle_data')
    fleet_vehicle_ids_count = fields.Integer(compute='_compute_fleet_vehicle_data')
    service_order_ids_count = fields.Integer(compute='_compute_fleet_vehicle_data')
    service_order_worksheet_count = fields.Integer(compute='_compute_fleet_vehicle_data')

    
    @api.depends('picking_ids.move_line_ids')
    def _compute_fleet_vehicle_data(self):
        for record in self:
            fleet_vehicle_ids = record.picking_ids.move_line_ids.fleet_vehicle_id
            record.fleet_vehicle_ids = fleet_vehicle_ids
            record.fleet_vehicle_ids_count = len(fleet_vehicle_ids.ids)
            record.service_order_ids_count = sum(fleet_vehicle_ids.mapped('service_order_ids_count'))
            record.service_order_worksheet_count = sum(fleet_vehicle_ids.mapped('service_order_worksheet_count'))

    def action_service_order_ids(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Service Orders'),
            'view_mode': 'tree,form',
            'res_model': 'service.order',
            'domain': [('id', 'in', self.fleet_vehicle_ids.service_order_ids.ids)]
        }
    
    def action_view_worksheets(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Worksheets'),
            'view_mode': 'tree',
            'res_model': 'service.order.worksheets',
            'context': {'service_order_ids': self.fleet_vehicle_ids.service_order_ids.ids},
            'target': 'current',
        }
    
    def action_fleet_vehicle(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicles',
            'view_mode': 'kanban,tree,form',
            'res_model': 'fleet.vehicle',
            'domain': [('id', 'in', self.fleet_vehicle_ids.ids)]
        }
