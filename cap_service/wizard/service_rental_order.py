from odoo import models, fields, api
from odoo.exceptions import UserError


class ServiceRentalOrder(models.TransientModel):
    _name = 'service.rental.order'
    _description = 'Service Rental Order'


    service_order_id = fields.Many2one('service.order')
    partner_id = fields.Many2one('res.partner')
    fleet_vehicle_id = fields.Many2one('fleet.vehicle')
    start_date = fields.Date()
    end_date = fields.Date()


    def button_save(self):
        sale_order = self.env['sale.order'].with_context({
            'in_rental_app':1,
            'search_default_from_rental': 1
            })
        line_vals = {
            'product_id': self.fleet_vehicle_id.product_id.id,
            'fleet_vehicle_rental_id': self.fleet_vehicle_id.id,
            'product_uom_qty': 1
        }
        vals = {
            'partner_id': self.partner_id.id,
            'order_line': [(0, 0, line_vals)],
            'rental_start_date': self.start_date,
            'rental_return_date': self.end_date,
            'origin': self.service_order_id.name,
            'service_order_rental_id': self.service_order_id.id
        }
        sale_order.create(vals).action_confirm()
        return self.service_order_id.action_stat_button_rental_order_ids()
