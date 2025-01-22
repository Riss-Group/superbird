from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'


    service_branch_id = fields.Many2one('res.company')
    parts_branch_id = fields.Many2one('res.company')
    sales_branch_id = fields.Many2one('res.company')
    default_service_order_internal_branch_id = fields.Many2one('res.company')
    available_service_branch_ids = fields.Many2many('res.company', compute="_compute_available_service_branch_ids")

    def _get_company_root_delegated_field_names(self):
        fnames = super()._get_company_root_delegated_field_names()
        return fnames + ['service_branch_id', 'parts_branch_id', 'sales_branch_id', 'default_service_order_internal_branch_id']

    @api.depends('root_id', 'all_child_ids')
    def _compute_available_service_branch_ids(self):
        for record in self:
            branches = record.root_id | record.all_child_ids
            record.available_service_branch_ids = branches