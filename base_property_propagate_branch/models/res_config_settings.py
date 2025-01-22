from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    autopropagate_properties = fields.Boolean(
        string="Auto-propagate Properties",
        related='company_id.autopropagate_properties',
        readonly=False
    )
    autopropagate_properties_name_search = fields.Boolean(
        string="Use name_search on AccessError",
        related='company_id.autopropagate_properties_name_search',
        readonly=False
    )

    @api.onchange('autopropagate_properties')
    def _onchange_autopropagate_properties(self):
        if not self.autopropagate_properties:
            self.autopropagate_properties_name_search = False