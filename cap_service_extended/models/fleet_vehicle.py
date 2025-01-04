
from odoo import  models, fields, api, _


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    # purchase fields
    chassis_built_date = fields.Date('Chassis Built Date')
    chassis_manufacturer_arrival_date = fields.Date('Chassis Manufacturer Arrival Date')
    bus_order_date = fields.Date('Bus Order Date', compute='_compute_dates')
    oem_production_date = fields.Date('OEM Production Date')
    revised_pick_up_date = fields.Date('Revised Pick-up Date', compute='_compute_dates')
    oem_ready_for_delivery_date = fields.Date('OEM Ready for Delivery Date') #TODO: confirm if it is to compute or it should be on stock move and not here?
    dealer_arrival_date = fields.Date('Dealer Arrival', compute='_compute_dates')
    pick_up_date = fields.Date('Pick-up Date', compute='_compute_dates')

    # sales field
    sold_customer_date = fields.Date('Sold Customer Date', compute='_compute_dates')
    sales_requested_delivery_date = fields.Date('Sales Requested Delivery Date', compute='_compute_dates')
    ready_for_delivery_date = fields.Date('Ready for Delivery Date', compute='_compute_dates')
    customer_delivered_date = fields.Date('Customer Delivered Date', compute='_compute_dates')

    # accounting fields
    oem_payment_due_date = fields.Date('OEM Payment Due Date', compute='_compute_dates')
    oem_body_payment_date = fields.Date('OEM Body Payment Date')
    oem_chassis_payment_date = fields.Date('OEM Chassis Payment Date')

    # service fields
    ready_for_inspection_date = fields.Date('Ready for Inspection Date', compute='_compute_service_date')
    in_service_date = fields.Date('In Service Date')


    @api.depends('fleet_move_line_ids')
    def _compute_dates(self):
        for rec in self:
            bus_order_date = False
            pick_up_date = False
            revised_pick_up_date = False
            oem_payment_due_date = False
            dealer_arrival_date = False
            sold_customer_date = False
            sales_requested_delivery_date = False
            ready_for_delivery_date = False
            customer_delivered_date = False
            for move_line in rec.sudo().fleet_move_line_ids:
                if move_line.picking_type_id.code == 'incoming':
                    purchase_order_ids = move_line.move_id.sudo().purchase_line_id.mapped('order_id')
                    bus_order_date = purchase_order_ids[0].date_approve or False
                    pick_up_date = purchase_order_ids[0].date_planned or False
                    revised_pick_up_date = move_line.move_id.date or False
                    oem_payment_due_date = purchase_order_ids[0].sudo().invoice_ids and purchase_order_ids[0].sudo().invoice_ids[0].invoice_date_due or False
                    dealer_arrival_date = move_line.picking_id.date_done or False
                if move_line.picking_type_id.code == 'outgoing':
                    sale_order_id = move_line.move_id.sudo().sale_line_id.mapped('order_id')
                    if sale_order_id:
                        sold_customer_date = sale_order_id[0].date_order or False
                        sales_requested_delivery_date = sale_order_id[0].commitment_date or False
                    ready_for_delivery_date = move_line.move_id.date or False
                    customer_delivered_date = move_line.picking_id.date_done or False
        rec.bus_order_date = bus_order_date
        rec.pick_up_date = pick_up_date
        rec.revised_pick_up_date = revised_pick_up_date
        rec.oem_payment_due_date = oem_payment_due_date
        rec.dealer_arrival_date = dealer_arrival_date
        rec.sold_customer_date = sold_customer_date
        rec.sales_requested_delivery_date = sales_requested_delivery_date
        rec.ready_for_delivery_date = ready_for_delivery_date
        rec.customer_delivered_date = customer_delivered_date

    @api.depends('service_order_ids')
    def _compute_service_date(self):
        for rec in self:
            rec.ready_for_inspection_date = rec.service_order_ids and rec.service_order_ids[0].start_date or False

