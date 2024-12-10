from odoo import fields, models, api
import numpy_financial as npf



class SaleFinanceTerms(models.Model):
    _name = 'sale.finance.terms'
    _description = 'Sale Finance Terms'
    _rec_name = 'order_id'


    order_id = fields.Many2one('sale.order')
    partner_id = fields.Many2one('res.partner', domain="[('financing_partner', '=', True)]")
    deposit_amount = fields.Float()
    trade_amount = fields.Float()
    finance_amount = fields.Float(compute="_compute_finance_amount", store=True, readonly=False)
    interest_rate_percent = fields.Float()
    skip_periods = fields.Integer()
    years_financed = fields.Integer(string='Years')
    terms_total = fields.Float(compute="_compute_terms_total", store=True, readonly=True)
    terms_interest_total = fields.Float(compute="_compute_terms_total", string="Interest Total", store=True, readonly=True)
    period_total = fields.Float(compute="_compute_terms_total", string="Period Amt", store=True, readonly=True)
    periodicity = fields.Selection(default='monthly', selection=[
        ('week', 'Weekly'),
        ('bi_week', 'Biweekly' ),
        ('monthly','Monthly')])

    
    @api.depends('order_id.amount_total', 'deposit_amount', 'trade_amount')
    def _compute_finance_amount(self):
        for record in self:
            record.finance_amount = record.order_id.amount_total - record.deposit_amount - record.trade_amount
        
    @api.depends('finance_amount', 'interest_rate_percent', 'skip_periods', 'years_financed', 'periodicity')
    def _compute_terms_total(self):
        for record in self:
            terms_total = 0
            terms_interest_total = 0
            period_total = 0
            if record.years_financed and record.interest_rate_percent and record.periodicity and record.finance_amount:
                periods_per_year = 1
                if record.periodicity == 'week':
                    periods_per_year = 52
                elif record.periodicity == 'bi_week':
                    periods_per_year = 26
                elif record.periodicity == 'monthly':
                    periods_per_year = 12
                if record.skip_periods and periods_per_year - record.skip_periods > 0:
                    periods_per_year = periods_per_year - record.skip_periods
                periodic_rate = record.interest_rate_percent / 100 / periods_per_year
                total_periods = record.years_financed * periods_per_year
                period_total = npf.pmt(periodic_rate, total_periods, -record.finance_amount)
                terms_total = period_total * total_periods
                terms_interest_total = (period_total * total_periods) - record.finance_amount

            record.terms_total = terms_total
            record.terms_interest_total = terms_interest_total
            record.period_total = period_total