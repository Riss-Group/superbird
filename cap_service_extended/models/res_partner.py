from odoo import  models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'


    def action_fleet_vehicle_ids(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicles',
            'view_mode': 'kanban,tree,form',
            'res_model': 'fleet.vehicle',
            'context': {'default_customer_id': self.id},
            'domain': [('customer_id', '=', self.id)]
        }