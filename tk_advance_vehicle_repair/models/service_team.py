# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _


class VehicleService(models.Model):
    """Vehicle Service"""
    _name = 'vehicle.service'
    _description = __doc__
    _rec_name = 'service_name'

    color = fields.Integer(default=1)
    service_name = fields.Char(string="Name", required=True, translate=True)
    service_charge = fields.Monetary(string="Service Charge")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")


class ServiceTeam(models.Model):
    """Service Team"""
    _name = 'service.team'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'title'

    color = fields.Integer()
    title = fields.Char(string="Title", required=True, translate=True)
    service_manager_id = fields.Many2one('res.users', default=lambda self: self.env.user, string="Responsible",
                                         required=True)
    team_member_ids = fields.Many2many('res.users', string="Team Members")
    service_team_project_id = fields.Many2one('project.project', readonly=True, store=True, string="Project")

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ServiceTeam, self).create(vals_list)
        project_id = self.env['project.project'].sudo().create({
            'name': res.title,
            'user_id': self.env.user.id,
            'company_id': self.env.company.id,
        })
        res.service_team_project_id = project_id.id
        return res


class VehicleServiceTeam(models.Model):
    """Vehicle Service Team"""
    _name = 'vehicle.service.team'
    _description = __doc__
    _rec_name = 'vehicle_service_id'

    vehicle_service_id = fields.Many2one('vehicle.service', string="Service", required=True)

    service_team_id = fields.Many2one('service.team', string="Team")
    member_ids = fields.Many2many(related="service_team_id.team_member_ids")
    vehicle_service_team_members_ids = fields.Many2many('res.users', string="Members",
                                                        domain="[('id', 'in', member_ids)]")

    start_date = fields.Date(string='Start Date', default=fields.date.today())
    end_date = fields.Date(string='End Date')
    team_project_id = fields.Many2one(related="service_team_id.service_team_project_id", string="Project")
    team_task_id = fields.Many2one('project.task', readonly=True, store=True)
    work_is_done = fields.Boolean(related='team_task_id.work_is_done', string="Work is Done")
    service_charge = fields.Monetary(string="Service Charge")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    repair_job_card_id = fields.Many2one('repair.job.card')

    @api.onchange('vehicle_service_id')
    def vehicle_service_charge(self):
        for rec in self:
            if rec.vehicle_service_id:
                rec.service_charge = rec.vehicle_service_id.service_charge

    def create_service_task(self):
        service_id = self.env['project.task'].sudo().create({
            'name': self.vehicle_service_id.service_name,
            'project_id': self.team_project_id.id,
            'partner_id': self.repair_job_card_id.customer_id.id,
            'user_ids': self.vehicle_service_team_members_ids.ids,
            'date_assign': self.start_date,
            'date_last_stage_update': self.end_date,
            'repair_job_card_id': self.repair_job_card_id.id
        })
        self.team_task_id = service_id.id

    @api.onchange('work_is_done')
    def _team_work_status(self):
        for record in self:
            if record.work_is_done:
                record.service_team_id = record.service_team_id
            else:
                record.service_team_id = False


class InspectionRepairTeam(models.Model):
    """Inspection Repair Team"""
    _name = 'inspection.repair.team'
    _description = __doc__
    _rec_name = 'vehicle_service_id'

    vehicle_service_id = fields.Many2one('vehicle.service', string="Service", required=True)

    service_team_id = fields.Many2one('service.team', string="Team")
    member_ids = fields.Many2many(related="service_team_id.team_member_ids")
    vehicle_service_team_members_ids = fields.Many2many('res.users', string="Members",
                                                        domain="[('id', 'in', member_ids)]")

    start_date = fields.Date(string='Start Date', default=fields.date.today())
    end_date = fields.Date(string='End Date')
    team_project_id = fields.Many2one(related="service_team_id.service_team_project_id", string="Project")
    team_task_id = fields.Many2one('project.task', readonly=True, store=True)
    work_is_done = fields.Boolean(related='team_task_id.work_is_done', string="Work is Done")
    service_charge = fields.Monetary(string="Service Charge")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    inspection_job_card_id = fields.Many2one('inspection.job.card')

    @api.onchange('vehicle_service_id')
    def vehicle_service_charge(self):
        for rec in self:
            if rec.vehicle_service_id:
                rec.service_charge = rec.vehicle_service_id.service_charge

    def create_service_task(self):
        service_id = self.env['project.task'].sudo().create({
            'name': self.vehicle_service_id.service_name,
            'project_id': self.team_project_id.id,
            'partner_id': self.inspection_job_card_id.customer_id.id,
            'user_ids': self.vehicle_service_team_members_ids.ids,
            'date_assign': self.start_date,
            'date_last_stage_update': self.end_date,
            'inspection_job_card_id': self.inspection_job_card_id.id
        })
        self.team_task_id = service_id.id

    @api.onchange('work_is_done')
    def _team_work_status(self):
        for record in self:
            if record.work_is_done:
                record.service_team_id = record.service_team_id
            else:
                record.service_team_id = False
