# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class InspectionJobCard(models.Model):
    """Inspection Job Card"""
    _name = 'inspection.job.card'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'inspection_number'

    inspection_number = fields.Char(string='Inspection No', readonly=True, default=lambda self: _('New'), copy=False)
    vehicle_brand_id = fields.Many2one('vehicle.brand', string="Vehicle", )
    vehicle_model_id = fields.Many2one('vehicle.model', string="Model",
                                       domain="[('vehicle_brand_id', '=', vehicle_brand_id)]", )
    vehicle_fuel_type_id = fields.Many2one('vehicle.fuel.type', string="Fuel Type")
    registration_no = fields.Char(string="Registration No", translate=True)
    vin_no = fields.Char(string="VIN No", translate=True)
    transmission_type = fields.Selection([('manual', "Manual"), ('automatic', "Automatic"), ('cvt', "CVT")],
                                         string="Transmission Type")

    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    street = fields.Char(string="Street", translate=True)
    street2 = fields.Char(string="Street 2", translate=True)
    city = fields.Char(string="City", translate=True)
    state_id = fields.Many2one("res.country.state", string="State")
    country_id = fields.Many2one("res.country", string="Country")
    zip = fields.Char(string="Zip")
    phone = fields.Char(string="Phone", translate=True)
    email = fields.Char(string="Email", translate=True)
    customer_observation = fields.Text(string="Customer Observation", translate=True)
    responsible_id = fields.Many2one('res.users', default=lambda self: self.env.user, required=True,
                                     string="Responsible")

    inspection_type = fields.Selection(
        [('full_inspection', "Full Inspection"), ('specific_inspection', "Specific Inspection")],
        default='full_inspection', string="Type of Inspection")

    inspect_type = fields.Selection([('only_inspection', "Only Inspection"),
                                     ('inspection_and_repair', "Inspection + Repair")], string="Inspection Type")

    part_assessment = fields.Boolean(string="Part Assessment")
    inner_body_inspection = fields.Boolean(string="Inner Body Inspection")
    outer_body_inspection = fields.Boolean(string="Outer Body Inspection")
    mechanical_condition = fields.Boolean(string="Mechanical Condition")
    vehicle_component = fields.Boolean(string="Vehicle Component")
    vehicle_fluid = fields.Boolean(string="Vehicle Fluid")
    tyre_inspection = fields.Boolean(string="Tyre Inspection")

    vehicle_booking_id = fields.Many2one('vehicle.booking', compute="_compute_vehicle_booking", string="Booking No")
    inspection_date = fields.Date(string="Date", required=True)
    inspection_charge = fields.Monetary(string="Inspection Charge")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")

    wd = fields.Boolean(string="4WD")
    abs = fields.Boolean(string="ABS")
    awd = fields.Boolean(string="AWD")
    gps = fields.Boolean(string="GPS")
    stereo = fields.Boolean(string="Stereo")
    bed_liner = fields.Boolean(string="Bedliner")
    wide_tires = fields.Boolean(string="Wide Tires")
    power_locks = fields.Boolean(string="Power Locks")
    power_seats = fields.Boolean(string="Power Seats")
    power_windows = fields.Boolean(string="Power Windows")
    running_boards = fields.Boolean(string="Running Boards")
    roof_rack = fields.Boolean(string="Roof Rack")
    camper_shell = fields.Boolean(string="Camper Shell")
    sport_wheels = fields.Boolean(string="Sport Wheels")
    tilt_wheel = fields.Boolean(string="Tilt Wheel")
    cruise_control = fields.Boolean(string="Cruise Control")
    cvt_transmission = fields.Boolean(string="CVT Transmission")
    infotainment_system = fields.Boolean(string="Infotainment System")
    moon_sun_roof = fields.Boolean(string="Moon or Sun Roof")
    rear_sliding_window = fields.Boolean(string="Rear Sliding Window")
    rear_window_wiper = fields.Boolean(string="Rear Window Wiper")
    rear_lift_gate = fields.Boolean(string="Rear Liftgate")
    air_conditioning = fields.Boolean(string="Air Conditioning")
    leather_interior = fields.Boolean(string="Leather Interior")
    towing_package = fields.Boolean(string="Towing Package")
    auto_transmission = fields.Boolean(string="Automatic Transmission")
    am_fm_radio = fields.Boolean(string="AM / FM / Sirius Radio")
    cd_usb_bluetooth = fields.Boolean(string="CD / USB / Bluetooth")
    luxury_sport_pkg = fields.Boolean(string="Luxury / Sport pkg.")
    other = fields.Boolean(string="Other")

    vehicle_condition_line_ids = fields.One2many('vehicle.condition.line', 'inspection_job_card_id')
    mechanical_item_condition_ids = fields.One2many('mechanical.item.condition', 'inspection_job_card_id')
    interior_item_condition_ids = fields.One2many('interior.item.condition', 'inspection_job_card_id')
    vehicle_components_ids = fields.One2many('vehicle.components', 'inspection_job_card_id')
    vehicle_fluids_ids = fields.One2many('vehicle.fluids', 'inspection_job_card_id')
    tyre_inspection_ids = fields.One2many('tyre.inspection', 'inspection_job_card_id', string="Tyre")
    vehicle_spare_part_ids = fields.One2many('vehicle.spare.part', 'inspection_job_card_id')
    inspection_repair_team_ids = fields.One2many('inspection.repair.team', 'inspection_job_card_id',
                                                 string="Service Details")

    repair_job_card_id = fields.Many2one('repair.job.card', string="Order Job Card No")

    stages = fields.Selection([('a_draft', "New"), ('b_in_progress', "In Progress"), ('c_complete', "Completed"),
                               ('d_cancel', "Cancelled")], default='a_draft', group_expand='_expand_groups')

    part_price = fields.Monetary(compute="_total_spare_part_price", string="Part Price")
    service_charge = fields.Monetary(compute="_inspection_repair_charges", string="Service Charges")
    sub_total = fields.Monetary(string="Sub Total", compute="_sub_total")
    team_task_count = fields.Integer(compute="_compute_team_task", string="Task")

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    sale_order_state = fields.Selection(related='sale_order_id.state', string="Order State")
    amount_total = fields.Monetary(related='sale_order_id.amount_total', string="Total Amount")

    inspection_repair_sale_order_id = fields.Many2one('sale.order', string=" Sale Order")
    repair_sale_order_state = fields.Selection(related='inspection_repair_sale_order_id.state')
    repair_amount_total = fields.Monetary(related='inspection_repair_sale_order_id.amount_total',
                                          string=" Total Amount")
    sale_invoiced = fields.Monetary()

    check_list_template_id = fields.Many2one('checklist.template', string="Checklist Template")
    inspection_checklist_ids = fields.One2many('inspection.checklist', 'inspection_job_card_id', string="Checklist")

    @api.model
    def _expand_groups(self, states, domain, order):
        return ['a_draft', 'b_in_progress', 'c_complete', 'd_cancel']

    def a_draft_to_b_in_progress(self):
        self.stages = 'b_in_progress'

    def b_in_progress_to_c_complete(self):
        self.ensure_one()
        template_id = self.env.ref("tk_advance_vehicle_repair.inspection_job_card_mail_template").sudo()
        ctx = {
            'default_model': 'inspection.job.card',
            'default_res_ids': self.ids,
            'default_partner_ids': [self.customer_id.id],
            'default_use_template': bool(template_id),
            'default_template_id': template_id.id,
            'default_composition_mode': 'comment',
            'default_email_from': self.env.company.email,
            'default_reply_to': self.env.company.email,
            'custom_layout': False,
            'force_email': True,
        }
        self.stages = 'c_complete'
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def c_complete_to_d_cancel(self):
        self.stages = 'd_cancel'

    def _compute_vehicle_booking(self):
        vehicle_booking_id = self.env['vehicle.booking'].search([('inspection_job_card_id', '=', self.id)], limit=1)
        self.vehicle_booking_id = vehicle_booking_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('inspection_number', _('New')) == _('New'):
                vals['inspection_number'] = self.env['ir.sequence'].next_by_code('inspection.job.card') or _('New')
        res = super(InspectionJobCard, self).create(vals_list)
        return res

    @api.depends('inspection_repair_team_ids')
    def _inspection_repair_charges(self):
        for rec in self:
            service_charge = 0.0
            if rec.inspection_repair_team_ids:
                for service in rec.inspection_repair_team_ids:
                    service_charge = service_charge + service.service_charge
                rec.service_charge = service_charge
            else:
                rec.service_charge = service_charge

    @api.depends('vehicle_spare_part_ids.unit_price', 'vehicle_spare_part_ids.qty')
    def _total_spare_part_price(self):
        for rec in self:
            part_price = 0.0
            if rec.vehicle_spare_part_ids:
                for part in rec.vehicle_spare_part_ids:
                    part_price = part_price + (part.unit_price * part.qty)
                rec.part_price = part_price
            else:
                rec.part_price = part_price

    @api.depends('sub_total', 'service_charge', 'part_price')
    def _sub_total(self):
        for rec in self:
            rec.sub_total = rec.service_charge + rec.part_price

    def create_repair_job_card(self):
        if not self.vehicle_brand_id or not self.registration_no or not self.vehicle_model_id:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _("Required: Vehicle, Registration No, and Model information."),
                    'sticky': False,
                }
            }
            return message
        data = {
            "vehicle_brand_id": self.vehicle_brand_id.id,
            "vehicle_model_id": self.vehicle_model_id.id,
            "vehicle_fuel_type_id": self.vehicle_fuel_type_id.id,
            "registration_no": self.registration_no,
            "vin_no": self.vin_no,
            "transmission_type": self.transmission_type,
            "inspect_repair_date": self.inspection_date,
            "customer_id": self.customer_id.id,
            "street": self.street,
            "street2": self.street2,
            "city": self.city,
            "state_id": self.state_id.id,
            "country_id": self.country_id.id,
            "zip": self.zip,
            "phone": self.phone,
            "email": self.email,
            "sub_total": self.sub_total,
        }
        repair_job_card_id = self.env['repair.job.card'].create(data)
        self.repair_job_card_id = repair_job_card_id.id
        for part in self.vehicle_spare_part_ids:
            v_part = {
                'product_id': part.product_id.id,
                'qty': part.qty,
                'unit_price': part.unit_price,
                'repair_job_card_id': repair_job_card_id.id
            }
            self.env['vehicle.order.spare.part'].create(v_part)

        for service in self.inspection_repair_team_ids:
            v_service = {
                'vehicle_service_id': service.vehicle_service_id.id,
                'service_team_id': service.service_team_id.id,
                'vehicle_service_team_members_ids': service.vehicle_service_team_members_ids.ids,
                'start_date': service.start_date,
                'end_date': service.end_date,
                'team_project_id': service.team_project_id.id,
                'team_task_id': service.team_task_id.id,
                'work_is_done': service.work_is_done,
                'service_charge': service.service_charge,
                'repair_job_card_id': repair_job_card_id.id,
            }
            self.env['vehicle.service.team'].create(v_service)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Repair Job Card'),
            'res_model': 'repair.job.card',
            'res_id': repair_job_card_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    @api.onchange('customer_id')
    def customer_details(self):
        for rec in self:
            if rec.customer_id:
                rec.phone = rec.customer_id.phone
                rec.email = rec.customer_id.email
                rec.street = rec.customer_id.street
                rec.street2 = rec.customer_id.street2
                rec.city = rec.customer_id.city
                rec.state_id = rec.customer_id.state_id
                rec.country_id = rec.customer_id.country_id
                rec.zip = rec.customer_id.zip

    def _compute_team_task(self):
        for rec in self:
            task_count = 0
            if rec.id:
                task_count = self.env['project.task'].sudo().search_count([('inspection_job_card_id', '=', rec.id)])
            rec.team_task_count = task_count

    def view_team_task(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tasks'),
            'view_mode': 'tree,form',
            'res_model': "project.task",
            'domain': [('inspection_job_card_id', '=', self.id)],
        }

    def only_inspection_charge(self):
        order_line = []
        for record in self:
            if record.inspection_charge == 0:
                raise ValidationError(_("Please inspection charge can not be zero"))
            else:
                inspection_record = {
                    'product_id': self.env.ref('tk_advance_vehicle_repair.vehicle_inspection').id,
                    'name': 'Vehicle Inspection',
                    'price_unit': self.inspection_charge,
                }
                order_line.append((0, 0, inspection_record)),
            data = {
                'partner_id': self.customer_id.id,
                'date_order': fields.Datetime.now(),
                'order_line': order_line,
            }
            sale_order_id = self.env['sale.order'].sudo().create(data)
            self.sale_order_id = sale_order_id.id
            return {
                'type': 'ir.actions.act_window',
                'name': _('Sale Order'),
                'res_model': 'sale.order',
                'res_id': sale_order_id.id,
                'view_mode': 'form',
                'target': 'current'
            }

    def action_inspection_repair_sale_order(self):
        total = self.service_charge + self.part_price
        order_line = []
        for part in self.vehicle_spare_part_ids:
            part_record = {
                'product_id': part.product_id.id,
                'product_uom_qty': part.qty,
                'price_unit': part.unit_price,
            }
            order_line.append((0, 0, part_record)),
        if self.service_charge > 0.0:
            service = ""
            for data in self.inspection_repair_team_ids:
                service = service + "{} - {} {}, \n".format(data.vehicle_service_id.service_name,
                                                            self.currency_id.symbol, data.service_charge)
            service_data = {
                'product_id': self.env.ref('tk_advance_vehicle_repair.vehicle_service_charge').id,
                'name': service,
                'price_unit': self.service_charge,
            }
            order_line.append((0, 0, service_data))
        data = {
            'partner_id': self.customer_id.id,
            'date_order': fields.Datetime.now(),
            'order_line': order_line,
        }
        if total > 0:
            inspection_repair_sale_order_id = self.env['sale.order'].sudo().create(data)
            self.inspection_repair_sale_order_id = inspection_repair_sale_order_id.id
            amount_total = inspection_repair_sale_order_id.amount_total
            self.sale_invoiced = amount_total
            return {
                'type': 'ir.actions.act_window',
                'name': _('Sale Order'),
                'res_model': 'sale.order',
                'res_id': inspection_repair_sale_order_id.id,
                'view_mode': 'form',
                'target': 'current'
            }
        else:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'title': _('Sale Order Value Cannot be Zero !'),
                    'sticky': False,
                }
            }
            return message

    @api.onchange('check_list_template_id')
    def get_checklist_items(self):
        for rec in self:
            if rec.check_list_template_id:
                checklist_items = []
                for item in rec.check_list_template_id.checklist_template_item_ids:
                    checklist_items.append((0, 0, {'name': item.name}))
                rec.inspection_checklist_ids = [(5, 0, 0)]
                rec.inspection_checklist_ids = checklist_items

    def unlink(self):
        for res in self:
            if res.stages != 'c_complete':
                res = super(InspectionJobCard, res).unlink()
                return res
            else:
                raise ValidationError(_('You cannot delete the completed order.'))
