
from odoo import  models, fields, api, _


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    # Technical info fields
    manufacturing_status = fields.Char(
        string="Manufacturing Status",
        readonly=True,
        help="This field is updated nightly from the OEM production system."
    )
    engine_id = fields.Many2one(
        'fleet.vehicle.engine',
        string="Engine",
        help="Select the engine information."
    )
    transmission_id = fields.Many2one(
        'fleet.vehicle.transmission',
        string="Transmission",
        help="Select the transmission information."
    )

    @api.depends('transmission_id', 'transmission_id.transmission_type', 'engine_id', 'engine_id.horsepower')
    def _compute_model_fields(self):
        super()._compute_model_fields()
        for rec in self.filtered(lambda x: x.engine_id and x.engine_id.horsepower):
            rec.horsepower = rec.engine_id.horsepower
        for rec in self.filtered(lambda x: x.transmission_id and x.transmission_id.transmission_type):
            rec.transmission = rec.transmission_id.transmission_type

    # purchase fields
    chassis_built_date = fields.Date('Chassis Built Date')
    chassis_manufacturer_arrival_date = fields.Date('Chassis Manufacturer Arrival Date')
    bus_order_date = fields.Date('Bus Order Date', compute='_compute_dates', store=True, readonly=False)
    oem_production_date = fields.Date('OEM Production Date')
    revised_pick_up_date = fields.Date('Revised Pick-up Date', compute='_compute_dates', store=True, readonly=False)
    oem_ready_for_delivery_date = fields.Date('OEM Ready for Delivery Date')  # TODO: confirm if it is to compute or move
    dealer_arrival_date = fields.Date('Dealer Arrival', compute='_compute_dates', store=True, readonly=False)
    pick_up_date = fields.Date('Pick-up Date', compute='_compute_dates', store=True, readonly=False)

    # sales field
    sold_customer_date = fields.Date('Sold Customer Date', compute='_compute_dates', store=True, readonly=False)
    sales_representative = fields.Many2one(
        'res.users',
        string="Sales Representative",
        help="The representative who sold the bus.",
        compute = '_compute_dates', store = True, readonly = False
    )
    sales_requested_delivery_date = fields.Date('Sales Requested Delivery Date', compute='_compute_dates', store=True, readonly=False)
    ready_for_delivery_date = fields.Date('Ready for Delivery Date', compute='_compute_dates', store=True, readonly=False)
    customer_delivered_date = fields.Date('Customer Delivered Date', compute='_compute_dates', store=True, readonly=False)

    # accounting fields
    oem_payment_due_date = fields.Date('OEM Payment Due Date', compute='_compute_dates', store=True, readonly=False)
    oem_body_payment_date = fields.Date('OEM Body Payment Date')
    oem_chassis_payment_date = fields.Date('OEM Chassis Payment Date')

    # service fields
    ready_for_inspection_date = fields.Date('Ready for Inspection Date', compute='_compute_service_date', store=True, readonly=False)
    in_service_date = fields.Date('In Service Date')


    @api.depends(
        'fleet_move_line_ids',
        'fleet_move_line_ids.picking_type_id.code',
        'fleet_move_line_ids.move_id.purchase_line_id.order_id',
        'fleet_move_line_ids.move_id.purchase_line_id.order_id.date_approve',
        'fleet_move_line_ids.move_id.purchase_line_id.order_id.date_planned',
        'fleet_move_line_ids.move_id.date',
        'fleet_move_line_ids.move_id.purchase_line_id.order_id.invoice_ids.invoice_date_due',
        'fleet_move_line_ids.picking_id.date_done',
        'fleet_move_line_ids.move_id.sale_line_id.order_id.date_order',
        'fleet_move_line_ids.move_id.sale_line_id.order_id.commitment_date'
    )
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
            sales_representative = False
            for move_line in rec.sudo().fleet_move_line_ids:
                if move_line.picking_type_id.code == 'incoming':
                    purchase_order_ids = move_line.move_id.purchase_line_id.mapped('order_id')
                    bus_order_date = purchase_order_ids and purchase_order_ids[0].date_approve or False
                    pick_up_date = purchase_order_ids and purchase_order_ids[0].date_planned or False
                    revised_pick_up_date = move_line.move_id.date or False
                    oem_payment_due_date = purchase_order_ids and purchase_order_ids.invoice_ids and purchase_order_ids[0].invoice_ids[0].invoice_date_due or False
                    dealer_arrival_date = move_line.picking_id.date_done or False
                if move_line.picking_type_id.code == 'outgoing':
                    sale_order_id = move_line.move_id.sale_line_id.mapped('order_id')
                    if sale_order_id:
                        sales_representative = sale_order_id.user_id
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
            rec.sales_representative = sales_representative
            rec.sales_requested_delivery_date = sales_requested_delivery_date
            rec.ready_for_delivery_date = ready_for_delivery_date
            rec.customer_delivered_date = customer_delivered_date

    @api.depends('service_order_ids.start_date')
    def _compute_service_date(self):
        for rec in self:
            rec.ready_for_inspection_date = rec.service_order_ids and rec.service_order_ids[0].start_date or False

