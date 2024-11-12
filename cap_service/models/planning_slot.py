from odoo import models, fields, api
from collections import defaultdict
from datetime import datetime


class PlanningSlot(models.Model):
    _inherit = 'planning.slot'

    service_order_line_id = fields.Many2one('service.order.line', store=True, readonly=False, related='sale_line_id.service_order_line_id', compute=False)
    service_task_id = fields.Many2one('project.task', store=True, readonly=False, related='sale_line_id.service_order_line_id.task_id', compute=False)
    service_project_id = fields.Many2one('project.project', string="Service Projects", store=True, readonly=False, related='sale_line_id.service_order_line_id.project_id', compute=False )

    @api.model
    def auto_plan_ids(self, view_domain):
        '''
            Override method to group planning slots by associated task, find the latest 
            `end_datetime` for each group, and update each task's `date_deadline` field accordingly.
        '''
        res = super().auto_plan_ids(view_domain=view_domain)
        slots = self.browse(res)
        task_slots = defaultdict(list)
        for slot in slots:
            task_slots[slot.service_task_id.id].append(slot)
        task_latest_end_date = {}
        for task_id, slots in task_slots.items():
            valid_end_dates = [slot.end_datetime for slot in slots if isinstance(slot.end_datetime, datetime)]
            if valid_end_dates:
                latest_end_date = max(valid_end_dates)
                task_latest_end_date[task_id] = latest_end_date
        for task_id, latest_end_date in task_latest_end_date.items():
            task = self.env['project.task'].browse(task_id)
            task.date_deadline = latest_end_date
        return res