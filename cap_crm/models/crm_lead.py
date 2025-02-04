from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    _order = "priority desc, expected_revenue desc"

    customer_reference = fields.Char("Customer Reference")

    @api.model_create_multi
    def create(self, vals_list):
        res = super(CrmLead, self).create(vals_list)
        for lead in res:
            if lead.partner_id and lead.partner_id.user_id and lead.partner_id.user_id != self.env.user:
                lead.create_activity_for_sales_person()
                self.env.user.notify_danger(message='Associated customer is already assigned to another sales person!')
        return res

    def create_activity_for_sales_person(self):
        self.partner_id.activity_schedule(
            activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,  # 'To Do' activity type
            summary="Opportunity Created",
            note="New opportunity created with associated customer for sales person : %s" % (self.user_id.name),
            user_id=self.partner_id.user_id.id,
        )

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
        if not self.partner_id:
            return self.env["ir.actions.actions"]._for_xml_id("sale_crm.crm_quotation_partner_action")

        # Pass customer_reference in context when creating a quotation
        action = super(
                    CrmLead,
                    self.with_context(customer_reference=self.customer_reference)
                ).action_sale_quotations_new()
        return action

