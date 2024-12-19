
from odoo import api, fields, models


class WarrantyClam(models.Model):
    _name = 'warranty.clam'
    _description = "Warranty Clam"


    partner_id = fields.Many2one('res.partner', string="Contact")
    warranty_clam_line_ids = fields.One2many('warranty.clam.line', 'warranty_clam_id', string="Warranty Clam Line")



class WarrantyClamLine(models.Model):
    _name = 'warranty.clam.line'
    _description = "Warranty Clam Line"

    warranty_clam_id = fields.Many2one('warranty.clam', string="Warranty Clam")