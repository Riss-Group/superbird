from odoo import models, api, fields, _
import logging
logger = logging.getLogger()

class ResPartner(models.Model):
    _inherit = 'res.partner'


    send_as_company_id = fields.Many2one('res.company')
    include_company_ids = fields.Many2many('res.company')
    due_move_ids = fields.One2many('account.move', string='Due Invoices', compute='_compute_due_invoice_ids')
    company_warning_message = fields.Html(compute='_compute_due_invoice_ids')
    current_due = fields.Monetary(string='Current', compute='_compute_aging_buckets')
    due_1_30 = fields.Monetary(string='1 to 30', compute='_compute_aging_buckets')
    due_31_60 = fields.Monetary(string='31 to 60', compute='_compute_aging_buckets')
    due_61_90 = fields.Monetary(string='61 to 90', compute='_compute_aging_buckets')
    due_91_120 = fields.Monetary(string='91 to 120', compute='_compute_aging_buckets')
    due_over_120 = fields.Monetary(string='Over 120', compute='_compute_aging_buckets')
    total_due = fields.Monetary(string='Total Due', compute='_compute_aging_buckets')

    @api.depends('unreconciled_aml_ids', 'send_as_company_id', 'include_company_ids')
    @api.depends_context('allowed_company_ids')
    def _compute_due_invoice_ids(self):
        for record in self:
            due_move_ids = self.env['account.move']
            warning_message = False
            report_company_ids = list(set(record.include_company_ids.ids + record.send_as_company_id.ids))
            context_allowed_company_ids = self.env.context.get('allowed_company_ids', [])
            missing_company_ids = list(set(report_company_ids) - set(context_allowed_company_ids))
            if missing_company_ids and not self.env.context.get('force_company_report'):
                report_company_ids = list(set(report_company_ids) & set(context_allowed_company_ids))
                missing_companies = self.env['res.company'].browse(missing_company_ids)
                missing_companies_with_invoices = self.env['res.company']
                for missing_company in missing_companies:
                    if record.with_company(missing_company).sudo().unreconciled_aml_ids.mapped('move_id'):
                        missing_companies_with_invoices += missing_company
                if missing_companies_with_invoices:
                    warning_message = '<div>The following companies are not included in the table below since they are not logged into:</div>'
                    warning_message += '<br/>'.join(missing_companies_with_invoices.mapped('name'))
                    warning_message += '<div>The printed report will show different values and as such it is recommended to log into the appropriate companies</div>'
            for company in report_company_ids:
                move_ids = record.with_company(company).sudo().unreconciled_aml_ids.mapped('move_id').filtered(lambda x: x.company_id.id == company)
                due_move_ids += move_ids
            record.due_move_ids = due_move_ids
            record.company_warning_message = warning_message
    
    @api.depends('due_move_ids')
    @api.depends_context('allowed_company_ids')
    def _compute_aging_buckets(self):
        today = fields.Date.today()
        for record in self:            
            res = record.get_aging_bucket(record.due_move_ids)
            record.current_due = res.get('current_due')
            record.due_1_30 = res.get('due_1_30')
            record.due_31_60 = res.get('due_31_60')
            record.due_61_90 = res.get('due_61_90')
            record.due_91_120 = res.get('due_91_120')
            record.due_over_120 = res.get('due_over_120')
            record.total_due = res.get('total_due')

    def get_aging_bucket(self, due_move_ids=False):
        self.ensure_one()
        today = fields.Date.today()
        current_due = 0.0
        due_1_30 = 0.0
        due_31_60 = 0.0
        due_61_90 = 0.0
        due_91_120 = 0.0
        due_over_120 = 0.0
        for move in due_move_ids:
            if move.state != 'posted' or move.payment_state == 'paid':
                continue
            days_due = (today - move.invoice_date_due).days
            amount_due = move.amount_residual
            if days_due <= 0:
                current_due += amount_due
            elif days_due <= 30:
                due_1_30 += amount_due
            elif days_due <= 60:
                due_31_60 += amount_due
            elif days_due <= 90:
                due_61_90 += amount_due
            elif days_due <= 120:
                due_91_120 += amount_due
            else:
                due_over_120 += amount_due
        return {
            'current_due' : current_due,
            'due_1_30' : due_1_30,
            'due_31_60' : due_31_60,
            'due_61_90' : due_61_90,
            'due_91_120' : due_91_120,
            'due_over_120' : due_over_120,
            'total_due' : current_due + due_1_30 + due_31_60 + due_61_90 + due_91_120 + due_over_120,
        }
    
