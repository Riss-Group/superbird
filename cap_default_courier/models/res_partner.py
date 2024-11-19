from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    default_courier_id = fields.Many2one('delivery.courier',string="Default Courier")
    default_ltl_id = fields.Many2one('delivery.courier',string="Default LTL")
