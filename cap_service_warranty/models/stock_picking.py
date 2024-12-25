from odoo import api, fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    warranty_claim_id = fields.Many2one('warranty.claim', string="Warranty Claim")


class StockMove(models.Model):
    _inherit = "stock.move"

    warranty_claim_line_id = fields.Many2one('warranty.claim.line', string="Warranty Claim Line")
