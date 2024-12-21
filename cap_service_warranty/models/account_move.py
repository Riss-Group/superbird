
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    warranty_claim_line_ids = fields.Many2many(
        'warranty.claim.line',
        'warranty_claim_line_invoice_rel',
        'invoice_line_id', 'warranty_claim_line_id',
        string='Warranty Claim Lines', readonly=True, copy=False)
