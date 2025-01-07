from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.model
    def default_get(self, fields):
        # Retrieve default values
        defaults = super(SaleOrder, self).default_get(fields)

        # Check for the opportunity ID in context to fetch customer_reference
        lead_id = self.env.context.get('default_opportunity_id')
        if lead_id:
            lead = self.env['crm.lead'].browse(lead_id)
            if lead.customer_reference:
                defaults['client_order_ref'] = lead.customer_reference

        return defaults
