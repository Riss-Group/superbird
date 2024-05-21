from odoo import  models, fields, api
from odoo.exceptions import UserError


class ServiceOrder(models.Model):
    _name = 'service.ccc'   
    _description = 'Cause Complaint Correction'

    ttype = fields.Selection([
        ('p', 'Complaint'),
        ('c', 'Cause'),
        ('r', 'Correction'),
    ], string='Type')
    option_num = fields.Integer()
    name = fields.Char()
    description = fields.Text()
    display_name = fields.Char(compute='_get_display_name')

    @api.depends('description')
    def _get_display_name(self):
        for rec in self:
            rec.display_name = rec.description