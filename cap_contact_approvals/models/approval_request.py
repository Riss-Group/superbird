from odoo import models, fields

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    bank_changed = fields.Boolean('Has Bank Info Changed')
    credit_limits_changed = fields.Boolean('Has Credit Limits Changed')
    allow_out_payment = fields.Boolean('Send Money')
    bank_ids = fields.One2many('res.partner.bank','approval_id',string='Banks')
    credit = fields.Float('Total Receivable')
    days_sales_outstanding = fields.Float('Days Sales Outstanding (DSO)')
    use_partner_credit_limit = fields.Boolean('Partner Limit')
    credit_limit = fields.Float(string='Credit Limit', help='Credit limit specific to this partner.',
        groups='account.group_account_invoice,account.group_account_readonly',
        company_dependent=True, copy=False, readonly=False)

    def action_approve(self, approver=None):
        # Use context to indicate that this update originates from an approval request
        partner_with_context = self.partner_id.with_context(origin='approval.request')

        if partner_with_context and partner_with_context.waiting_on_approval:
            partner_vals = {}

            # Process credit limit changes if applicable
            if self.credit_limits_changed:
                partner_vals.update({
                    'use_partner_credit_limit': self.use_partner_credit_limit,
                    'credit_limit': self.credit_limit,
                })

            # Process each bank_ids command
            if self.bank_changed:
                for bank in self.bank_ids.with_context(origin='approval.request'):
                    if bank.command == 0:  # Create
                        bank_data = {
                            'acc_number': bank.acc_number,
                            'allow_out_payment': bank.allow_out_payment,
                            'acc_holder_name': bank.acc_holder_name,
                            'partner_id': partner_with_context.id  # Assign to the actual partner
                        }
                        self.env['res.partner.bank'].create(bank_data)

                    elif bank.command == 1:  # Update
                        existing_bank = self.env['res.partner.bank'].browse(bank.id)
                        if existing_bank:
                            existing_bank.with_context(origin='approval.request').write({
                                'acc_number': bank.acc_number,
                                'allow_out_payment': bank.allow_out_payment,
                                'acc_holder_name': bank.acc_holder_name,
                            })

                    elif bank.command == 2:  # Delete
                        existing_bank = self.env['res.partner.bank'].browse(bank.id)
                        if existing_bank:
                            existing_bank.with_context(origin='approval.request').unlink()

            # Write updated values to the partner and reset approval flag
            if partner_vals:
                partner_with_context.write(partner_vals)
            partner_with_context.waiting_on_approval = False

        return super(ApprovalRequest, self).action_approve(approver)

    def action_refuse(self):
        partner_with_context = self.partner_id.with_context(origin='approval.request')

        # Remove any temporary bank records that were created and linked to this approval if the approval is refused
        for bank in self.bank_ids:
            if bank.command == 0:
                bank.with_context(origin='approval.refuse').unlink()

        partner_with_context.waiting_on_approval = False

        return super(ApprovalRequest, self).action_refuse()
