from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    autopropagate_properties = fields.Boolean(
        string="Auto-propagate Properties to child branches",
        default=False,
        help="Enable or disable automatic propagation of ir.property to child branches."
    )
    autopropagate_properties_name_search = fields.Boolean(
        string="Use name_search on AccessError",
        default=False,
        help="If a property is not shared to a child branch, find a matching with the same name to use."
    )
    autopropagate_properties_all = fields.Boolean(
        string="Auto-propagate Properties to all companies",
        default=False,
        help="Set properties for all other companies"
    )