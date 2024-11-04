from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    customer_reference = fields.Char("Customer Reference")

    @api.constrains('customer_reference')
    def _check_customer_reference_unique(self):
        for lead in self:
            if lead.customer_reference:
                # Only check for duplicates within crm.lead
                duplicate_leads = self.search([
                    ('customer_reference', '=', lead.customer_reference),
                    ('id', '!=', lead.id)
                ])
                if duplicate_leads:
                    raise UserError(
                        _("Customer Reference must be unique among Leads. Please update the Customer Reference value"))

    def write(self, vals):
        res = super(CrmLead, self).write(vals)
        if 'customer_reference' in vals:
            for lead in self:
                # Find related sale order if exists and update client_order_ref
                sale_order = self.env['sale.order'].search([('opportunity_id', '=', lead.id)], limit=1)
                if sale_order:
                    sale_order.client_order_ref = lead.customer_reference
        return res

    def action_sale_quotations_new(self):
        raise UserError("test")
        # Redirect to add partner if none exists
        if not self.partner_id:
            return self.env["ir.actions.actions"]._for_xml_id("sale_crm.crm_quotation_partner_action")

        # Pass customer_reference in context when creating a quotation
        action = super(
                    CrmLead,
                    self.with_context(customer_reference=self.customer_reference, opportunity_id=self.id)
                ).action_sale_quotations_new()
        return action

class CRMStage(models.Model):
    _inherit = 'crm.stage'

    is_proposition = fields.Boolean(string="Is Proposition")

    def write(self, vals):
        print(f"\n\n{vals}\n\n")
        if vals.get('is_proposition'):
            proposition_stage = self.env['crm.stage'].search([('is_proposition','=',True)],limit=1)
            if proposition_stage:
                raise UserError(f"""Only 1 stage can be configured as the Proposition Stage. If you would like to make the '{self.name}' the proposition stage then re-configure the '{proposition_stage.name}' stage.""")
        return super(CRMStage, self).write(vals)
