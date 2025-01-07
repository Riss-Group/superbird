from odoo import fields, api, models

class CrmLead(models.Model):
    _inherit = 'crm.lead'


    def action_sale_quotations_new(self):
        action = super(
                    CrmLead,
                    self.with_context(opportunity_id=self.id)
                ).action_sale_quotations_new()
        return action
