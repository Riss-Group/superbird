from odoo import  models, fields, api
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'
    _order = "priority desc, planned_date_begin desc, id desc"
    

    name = fields.Char(string='Description')
    cause = fields.Char()
    correction = fields.Char()
    priority = fields.Selection(selection_add=[
        ('1','low'),
        ('2','med-low'),
        ('3','med'),
        ('4','med-high'),
        ('5','high'),
    ],default='1')
    planning_slot_ids = fields.One2many('planning.slot', 'service_task_id')

class ProjectTaskCreateTimesheet(models.TransientModel):
    _inherit = 'project.task.create.timesheet'

    cause = fields.Char()
    correction = fields.Char()

    def save_timesheet(self):
        aa_line_ids = super().save_timesheet()
        self.task_id.cause = self.cause
        self.task_id.correction = self.correction
        aa_line_ids.name = self.correction
        return aa_line_ids
