from odoo import  models, fields, api
from odoo.exceptions import UserError
import logging
logger = logging.getLogger()

class ProjectProject(models.Model):
    _inherit = 'project.project'
    

    is_repair_service = fields.Boolean(string="Repair Service")
    branch_company_ids = fields.Many2many('res.company', compute="_compute_branch_company_ids", store=True, readonly=False)

    @api.depends('company_id')
    def _compute_branch_company_ids(self):
        for record in self:
            if record.company_id:
                company_id = record.company_id.parent_id if record.company_id.parent_id else record.company_id
                linked_companies = [
                    company_id.service_branch_id,
                    company_id.parts_branch_id,
                    company_id.sales_branch_id,
                    company_id
                ]
                record.branch_company_ids = [(6, 0, {c.id for c in linked_companies if c})]
            else:
                record.branch_company_ids = [(5,)] 

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if defaults.get('is_repair_service'):
            defaults['allow_quotations'] = False
        return defaults

    @api.depends('is_fsm', 'is_repair_service')
    def _compute_allow_quotations(self):
        super()._compute_allow_quotations()
        for record in self:
            record.allow_quotations = not record.is_repair_service

    @api.depends('is_fsm', 'allow_material', 'is_repair_service')
    def _compute_allow_billable(self):
        super()._compute_allow_billable()
        for project in self:
            project.allow_billable = not project.is_repair_service

    @api.depends('allow_billable', 'is_fsm', 'is_repair_service')
    def _compute_allow_material(self):
        super()._compute_allow_material()
        for project in self:
            project.allow_material = not project.is_repair_service
    
    @api.model_create_multi
    def create(self, vals):
        records = super().create(vals)
        for rec in records.filtered(lambda x: x.is_repair_service):
            task_stage_ids = self.env['project.task.type']
            task_stage_ids += self.env.ref('cap_service.service_task_stage_new', raise_if_not_found=False)
            task_stage_ids += self.env.ref('cap_service.service_task_stage_wip', raise_if_not_found=False)
            task_stage_ids += self.env.ref('cap_service.service_task_stage_done', raise_if_not_found=False)
            rec.type_ids = task_stage_ids.ids
        return records