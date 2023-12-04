# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class CheckListTemplateItems(models.Model):
    """Check List Template Items"""
    _name = 'checklist.template.item'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Title", required=True)
    checklist_template_id = fields.Many2one('checklist.template')


class ChecklistTemplate(models.Model):
    """Check List Template"""
    _name = 'checklist.template'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, translate=True)
    checklist_template_item_ids = fields.One2many('checklist.template.item', 'checklist_template_id',
                                                  string="Checklist Items")


class InspectionChecklist(models.Model):
    """Inspection Check list"""
    _name = 'inspection.checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, translate=True)
    description = fields.Char(string="Description", translate=True)
    is_check = fields.Boolean(string="Check")
    inspection_job_card_id = fields.Many2one('inspection.job.card')

    @api.onchange('is_check')
    def inspection_checklist_check(self):
        for rec in self:
            if rec.is_check:
                rec.name = rec.name
            else:
                rec.name = False


class RepairChecklist(models.Model):
    """Repair Check list"""
    _name = 'repair.checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, translate=True)
    description = fields.Char(string="Description", translate=True)
    is_check = fields.Boolean(string="Check")
    repair_job_card_id = fields.Many2one('repair.job.card')

    @api.onchange('is_check')
    def repair_checklist_check(self):
        for rec in self:
            if rec.is_check:
                rec.name = rec.name
            else:
                rec.name = False
