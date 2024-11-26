from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model_create_multi
    def create(self, vals):
        res = super(SaleOrder,self).create(vals)
        opportunity = self.env['crm.lead'].browse(self.env.context.get('default_opportunity_id'))
        if opportunity:
            # Upon Creation opportunity.order_ids is init however not self so we must account for this
            has_quotations = len(opportunity.order_ids) - 1
            if has_quotations < 1:
                prop_stage = self.env['crm.stage'].search([('is_proposition','=',True)],limit=1)
                if prop_stage:
                    opportunity.stage_id = prop_stage
        return res

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.opportunity_id:
            if self.opportunity_id.stage_id.name != 'Won':
                self.opportunity_id.stage_id = self.env.ref("crm.stage_lead4").id
        return res
