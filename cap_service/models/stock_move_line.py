from odoo import models, fields, api
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'


    fleet_vehicle_id = fields.Many2one('fleet.vehicle',compute='_compute_fleet_vehicle_id',store=True, readonly=False)
    service_ack = fields.Boolean(string="Service Acknowledged", readonly=False)

    @api.depends('lot_id','lot_name')
    def _compute_fleet_vehicle_id(self):
        for record in self:
            fleet_vehicle_id = False
            if record.product_id.create_fleet_vehicle:
                if record.lot_id:
                    fleet_vehicle_id = record.env['fleet.vehicle'].search([('stock_number','=',record.lot_id.name)])
                elif record.lot_name:
                    fleet_vehicle_id = record.env['fleet.vehicle'].search([('stock_number','=',record.lot_name)])
            record.fleet_vehicle_id = fleet_vehicle_id

    def _action_done(self):
        super()._action_done()
        for record in self:
            if record.product_id.create_fleet_vehicle and record.picking_type_id.code == 'incoming' and record.lot_name:
                record._process_fleet_vehicle_in()
            elif record.product_id.create_fleet_vehicle and record.picking_type_id.code == 'outgoing' and record.lot_id:
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
                'product_id': self.product_id.id,
                'company_id': self.picking_id.company_id.id       
            })

    def _process_fleet_vehicle_out(self):
        self.ensure_one()
        lot_name = self.lot_name or self.lot_id.name
        fleet_vehicle_id = self.env['fleet.vehicle'].search([('stock_number','=',lot_name)])
        if fleet_vehicle_id:
            self.fleet_vehicle_id = fleet_vehicle_id
            vals = {
                'customer_id': self.picking_id.partner_id.id,
                'sold_date': self.picking_id.scheduled_date,
            }
            if not fleet_vehicle_id.has_outgoing_package_service and self.service_ack:
                package_product_ids = self.picking_id.sale_id.order_line.filtered(lambda x:x.product_id.package_service_template_id).product_id
                if package_product_ids:
                    service_vals = {
                    'end_date' : self.picking_id.scheduled_date,
                    'partner_id' : self.picking_id.company_id.partner_id.id,
                    'fleet_vehicle_id' : fleet_vehicle_id.id,
                    'company_id':self.company_id.service_branch_id.id
                    }
                    if fields.Datetime.now() > self.picking_id.scheduled_date:
                        service_vals.update({'start_date': self.picking_id.scheduled_date})
                    service_order_id = self.env['service.order'].create(service_vals)
                    service_order_id.message_post(body="Service Order auto-generated for outgoing PDI Delivery", subtype_xmlid='mail.mt_note')
                    service_order_id._onchange_fleet_vehicle_id()
                    service_template_select = self.env['service.template.select'].create({
                        'service_order_id': service_order_id.id,
                        'service_template': [(6,0,package_product_ids.package_service_template_id.ids)]
                    })
                    service_template_select.button_save()
                    service_order_id.action_upsert_so()
                    service_order_id.action_create_tasks()                
                    vals.update({'has_outgoing_package_service': True})
            if not fleet_vehicle_id.has_outgoing_pdi and self.product_id.create_pdi_delivery and self.service_ack:
                fleet_vehicle_id._create_fleet_pdi(direction='out')
            if vals:
                fleet_vehicle_id.write(vals)