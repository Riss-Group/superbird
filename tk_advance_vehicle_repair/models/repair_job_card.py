# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _


class ProjectTask(models.Model):
    """Project Task"""
    _inherit = 'project.task'
    _description = __doc__

    repair_job_card_id = fields.Many2one('repair.job.card', string=" Job Card")
    r_vehicle_brand_id = fields.Many2one(related='repair_job_card_id.vehicle_brand_id', string=" Vehicle")
    r_vehicle_model_id = fields.Many2one(related='repair_job_card_id.vehicle_model_id', string=" Model")
    r_vehicle_fuel_type_id = fields.Many2one(related='repair_job_card_id.vehicle_fuel_type_id', string=" Fuel Type")
    r_registration_no = fields.Char(related='repair_job_card_id.registration_no', string=" Registration No",
                                    translate=True)
    r_vin_no = fields.Char(related='repair_job_card_id.vin_no', string=" VIN No", translate=True)
    r_transmission_type = fields.Selection(related='repair_job_card_id.transmission_type', string=" Transmission Type")
    work_is_done = fields.Boolean(string="Work is Done")

    inspection_job_card_id = fields.Many2one('inspection.job.card', string="Job Card")
    i_vehicle_brand_id = fields.Many2one(related='inspection_job_card_id.vehicle_brand_id', string="Vehicle")
    i_vehicle_model_id = fields.Many2one(related='inspection_job_card_id.vehicle_model_id', string="Model")
    i_vehicle_fuel_type_id = fields.Many2one(related='inspection_job_card_id.vehicle_fuel_type_id', string="Fuel Type")
    i_registration_no = fields.Char(related='inspection_job_card_id.registration_no', string="Registration No",
                                    translate=True)
    i_vin_no = fields.Char(related='inspection_job_card_id.vin_no', string="VIN No", translate=True)
    i_transmission_type = fields.Selection(related='inspection_job_card_id.transmission_type',
                                           string="Transmission Type")


class RepairJobCard(models.Model):
    """Repair Job Card"""
    _name = 'repair.job.card'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'sequence_number'

    sequence_number = fields.Char(string='Sequence No', readonly=True, default=lambda self: _('New'), copy=False)
    vehicle_brand_id = fields.Many2one('vehicle.brand', string="Vehicle")
    vehicle_model_id = fields.Many2one('vehicle.model', string="Model",
                                       domain="[('vehicle_brand_id', '=', vehicle_brand_id)]")
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

    inspect_repair_date = fields.Date(string="Date", required=True)
    inspection_job_card_id = fields.Many2one('inspection.job.card', string="Job Card No",
                                             compute='_compute_vehicle_inspection_job_card')
    vehicle_booking_id = fields.Many2one('vehicle.booking', compute="_compute_vehicle_booking", string="Booking No")

    vehicle_order_spare_part_ids = fields.One2many('vehicle.order.spare.part', 'repair_job_card_id')
    vehicle_service_team_ids = fields.One2many('vehicle.service.team', 'repair_job_card_id')

    part_price = fields.Monetary(compute="_total_spare_part_price", string="Part Price")
    service_charge = fields.Monetary(compute="_vehicle_service_charge", string="Service Charges")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    sub_total = fields.Monetary(string="Sub Total", compute="_sub_total")
    team_task_count = fields.Integer(compute="_compute_team_task_count", string="Task")

    repair_sale_order_id = fields.Many2one('sale.order', string=" Sale Order")
    repair_order_state = fields.Selection(related='repair_sale_order_id.state')
    repair_amount = fields.Monetary(related='repair_sale_order_id.amount_total', string=" Total Amount")
    repair_sale_invoiced = fields.Monetary()

    stages = fields.Selection(
        [('draft', "New"), ('assign_to_technician', "Assign to Technician"), ('in_diagnosis', "In Diagnosis"),
         ('supervisor_inspection', "In Supervisor Inspection"), ('complete', "Complete"), ('hold', "Hold"),
         ('cancel', "Cancel")], default='draft', string="Stages", group_expand='_expand_groups')

    check_list_template_id = fields.Many2one('checklist.template', string="Checklist Template")
    repair_checklist_ids = fields.One2many('repair.checklist', 'repair_job_card_id', string="Checklist")

    @api.model
    def _expand_groups(self, states, domain, order):
        return ['draft', 'assign_to_technician', 'in_diagnosis', 'supervisor_inspection', 'complete', 'hold', 'cancel']

    def _compute_team_task_count(self):
        for rec in self:
            task_counts = 0
            if rec.id:
                task_counts = self.env['project.task'].sudo().search_count(
                    [('repair_job_card_id', '=', rec.id)])
            rec.team_task_count = task_counts + rec.inspection_job_card_id.team_task_count

    def view_team_tasks(self):
        ids = self.inspection_job_card_id.inspection_repair_team_ids.mapped('team_task_id').mapped('id')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tasks'),
            'view_mode': 'tree,form',
            'res_model': "project.task",
            'domain': ['|', ('repair_job_card_id', '=', self.id), ('id', 'in', ids)],
        }

    def draft_to_assign_to_technician(self):
        self.stages = 'assign_to_technician'

    def assign_to_technician_to_in_diagnosis(self):
        self.stages = 'in_diagnosis'

    def in_diagnosis_to_supervisor_inspection(self):
        team_work_complete = True
        for rec in self.vehicle_service_team_ids:
            if not rec.work_is_done:
                team_work_complete = False
                break
        if not team_work_complete:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'title': _('Team Works'),
                    'message': "Please complete Team Work",
                    'sticky': False,
                }
            }
            return message
        else:
            self.stages = 'supervisor_inspection'

    def supervisor_inspection_to_complete(self):
        self.ensure_one()
        template_id = self.env.ref("tk_advance_vehicle_repair.repair_job_card_mail_template").sudo()
        ctx = {
            'default_model': 'repair.job.card',
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
        self.stages = 'complete'
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def complete_to_hold(self):
        self.stages = 'hold'

    def hold_to_cancel(self):
        self.stages = 'cancel'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence_number', _('New')) == _('New'):
                vals['sequence_number'] = self.env['ir.sequence'].next_by_code('repair.job.card') or _('New')
        res = super(RepairJobCard, self).create(vals_list)
        return res

    def _compute_vehicle_booking(self):
        vehicle_booking_id = self.env['vehicle.booking'].search([('repair_job_card_id', '=', self.id)], limit=1)
        self.vehicle_booking_id = vehicle_booking_id.id

    def _compute_vehicle_inspection_job_card(self):
        inspection_job_card_id = self.env['inspection.job.card'].search(
            [('repair_job_card_id', '=', self.id)], limit=1)
        self.inspection_job_card_id = inspection_job_card_id.id

    @api.depends('vehicle_service_team_ids')
    def _vehicle_service_charge(self):
        for rec in self:
            service_charge = 0.0
            if rec.vehicle_service_team_ids:
                for service in rec.vehicle_service_team_ids:
                    service_charge = service_charge + service.service_charge
                rec.service_charge = service_charge
            else:
                rec.service_charge = service_charge

    @api.depends('vehicle_order_spare_part_ids.unit_price', 'vehicle_order_spare_part_ids.qty')
    def _total_spare_part_price(self):
        for rec in self:
            part_price = 0.0
            if rec.vehicle_order_spare_part_ids:
                for part in rec.vehicle_order_spare_part_ids:
                    part_price = part_price + (part.unit_price * part.qty)
                rec.part_price = part_price
            else:
                rec.part_price = part_price

    @api.depends('sub_total', 'service_charge', 'part_price')
    def _sub_total(self):
        for rec in self:
            rec.sub_total = rec.service_charge + rec.part_price

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

    def action_repair_sale_order(self):
        total = self.service_charge + self.part_price
        order_line = []
        for part in self.vehicle_order_spare_part_ids:
            part_record = {
                'product_id': part.product_id.id,
                'product_uom_qty': part.qty,
                'price_unit': part.unit_price,
            }
            order_line.append((0, 0, part_record)),
        if self.service_charge > 0.0:
            service = ""
            for data in self.vehicle_service_team_ids:
                service = service + "{} - {} {}, \n".format(data.vehicle_service_id.service_name,
                                                            self.currency_id.symbol,
                                                            data.service_charge)
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
            repair_sale_order_id = self.env['sale.order'].sudo().create(data)
            self.repair_sale_order_id = repair_sale_order_id.id
            amount_total = repair_sale_order_id.amount_total
            self.repair_sale_invoiced = amount_total
            return {
                'type': 'ir.actions.act_window',
                'name': _('Sale Order'),
                'res_model': 'sale.order',
                'res_id': repair_sale_order_id.id,
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
                rec.repair_checklist_ids = [(5, 0, 0)]
                rec.repair_checklist_ids = checklist_items

    def unlink(self):
        for res in self:
            if res.stages != 'complete':
                res = super(RepairJobCard, res).unlink()
                return res
            else:
                raise ValidationError(_('You cannot delete the completed order.'))
