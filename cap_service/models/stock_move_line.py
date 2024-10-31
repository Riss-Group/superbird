from odoo import models, fields, api
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'


    fleet_vehicle_id = fields.Many2one('fleet.vehicle')

    def _action_done(self):
        super()._action_done()
        for record in self:
            if record.product_id.create_fleet_vehicle and record.picking_type_id.code == 'incoming' and record.lot_name:
                record._process_fleet_vehicle_in()
            elif record.product_id.create_fleet_vehicle and record.picking_type_id.code == 'outgoing' and record.lot_name:
                record._process_fleet_vehicle_out()
    
    def _process_fleet_vehicle_in(self):
        self.ensure_one()
        fleet_vehicle_id = self.fleet_vehicle_id or self.env['fleet.vehicle'].search([('stock_number','=',self.lot_name)])
        if not fleet_vehicle_id:
            self.fleet_vehicle_id = fleet_vehicle_id.create({
                'model_id': self.product_id.vehicle_model_id.id,
                'model_year': self.product_id.vehicle_year,
                'customer_id': self.picking_id.company_id.partner_id.id,
                'stock_number': self.lot_name,
                'acquisition_date':False,
                'order_date' : self.picking_id.scheduled_date,   
                'product_id': self.product_id.id           
            })

    def _process_fleet_vehicle_out(self):
        self.ensure_one()
        fleet_vehicle_id = self.env['fleet.vehicle'].search([('stock_number','=',self.lot_name)])
        if fleet_vehicle_id:
            self.fleet_vehicle_id = fleet_vehicle_id
            fleet_vehicle_id.write({
                'customer_id': self.picking_id.partner_id.id,
                'sold_date': self.picking_id.scheduled_date,
            })