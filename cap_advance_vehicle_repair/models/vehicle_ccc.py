from odoo import models, fields, api


class VehicleCCC(models.Model):
    _name = 'vehicle.ccc'
    _description = 'Vehicle Cause Complaint Correction'

    ttype = fields.Selection([
        ('p', 'Complaint'),
        ('c', 'Cause'),
        ('r', 'Correction'),
    ], string='Type')
    option_num = fields.Integer()
    name = fields.Char()
    description = fields.Text()
    display_name = fields.Char(compute='_get_display_name')

    #Lazy hack to display actual CCC. todo: remove at some point
    @api.depends('description')
    def _get_display_name(self):
        for rec in self:
            rec.display_name = rec.description
    