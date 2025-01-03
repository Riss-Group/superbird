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

    def _action_cancel(self):
        res = super(SaleOrder, self)._action_cancel()
        if self.opportunity_id:
            if not self.opportunity_id.stage_id.is_lost:
                lost_stage_id = self.env['crm.stage'].search([('is_lost', '=', True)], limit=1)
                if lost_stage_id:
                    self.opportunity_id.stage_id = lost_stage_id.id
        return res

    def _compute_is_expired(self):
        super(SaleOrder, self)._compute_is_expired()
        today = fields.Date.today()
        for order in self:
            if (order.state in ('draft', 'sent') and order.validity_date and order.validity_date < today and
                    order.opportunity_id and not order.opportunity_id.stage_id.is_lost):
                lost_stage_id = self.env['crm.stage'].search([('is_lost', '=', True)], limit=1)
                if lost_stage_id:
                    order.opportunity_id.stage_id = lost_stage_id.id