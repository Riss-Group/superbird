from odoo import models, fields, api
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'


    fleet_vehicle_id = fields.Many2one('fleet.vehicle')


    def _action_done(self):
        super()._action_done()
        for record in self:
            if record.product_id.create_fleet_vehicle and record.picking_type_id.code == 'incoming' and record.lot_id:
                fleet_vehicle_id = self.env['fleet.vehicle'].search([('body_number','=',record.lot_id.name)])
                if not fleet_vehicle_id:
                    record.fleet_vehicle_id = fleet_vehicle_id.create({
                        'model_id': record.product_id.vehicle_model_id.id,
                        'model_year': record.product_id.vehicle_year,
                        'customer_id': record.picking_id.company_id.partner_id.id,
                        'body_number': record.lot_id.name,
                        'acquisition_date':False,
                        'order_date' : record.picking_id.scheduled_date,   
                        'product_id': record.product_id.id           
                    })
            elif record.product_id.create_fleet_vehicle and record.picking_type_id.code == 'outgoing' and record.lot_id:
                fleet_vehicle_id = self.env['fleet.vehicle'].search([('body_number','=',record.lot_id.name)])
                if fleet_vehicle_id:
                    record.fleet_vehicle_id = fleet_vehicle_id
                    fleet_vehicle_id.write({
                        'customer_id': record.picking_id.partner_id.id,
                        'sold_date': record.picking_id.scheduled_date,
                    })