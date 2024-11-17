from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    waiting_on_approval = fields.Boolean(string="Waiting on Approval")

    def write(self, vals):
        bank_fields = {'bank_ids', 'acc_number', 'allow_payment', 'acc_holder_name'}
        credit_fields = {'credit', 'days_sales_outstanding', 'use_partner_credit_limit', 'credit_limit'}

        field_keys = set(bank_fields | credit_fields)
        val_keys = set(vals.keys())

        if field_keys & val_keys and not self.waiting_on_approval:
            category = self.env['approval.category'].search(
                [('name', '=', 'Change Contact Accounting Info')],
                limit=1
            )
            if not category:
                raise UserError("Approval category 'Change Contact Accounting Info' is not defined.")

            for partner in self:
                approval = self.env['approval.request'].create({
                    'date': fields.Datetime.now(),
                    'partner_id': partner.id,
                    'category_id': category.id,
                    'bank_changed': bool(bank_fields & val_keys),
                    'credit_limits_changed': bool(credit_fields & val_keys),
                })

                bank_ids_commands = vals.get('bank_ids', [])
                for command in bank_ids_commands:
                    if command[0] == 0:  # CREATE
                        bank_data = command[2].copy()
                        bank_data.update({
                            'partner_id': 1,  # Temporarily set to OdooBot
                            'approval_id': approval.id,
                            'command': 0,
                        })
                        self.env['res.partner.bank'].create(bank_data)

                    elif command[0] == 1:  # UPDATE
                        bank_id = command[1]
                        update_vals = command[2]
                        update_vals.update({
                            'approval_id': approval.id,
                            'command': 1,
                        })
                        existing_bank = self.env['res.partner.bank'].browse(bank_id)
                        if existing_bank:
                            existing_bank.write(update_vals)

                    elif command[0] == 2:  # DELETE
                        bank_id = command[1]
                        update_vals = {
                            'approval_id': approval.id,
                            'command': 2,
                        }
                        existing_bank = self.env['res.partner.bank'].browse(bank_id)
                        if existing_bank:
                            existing_bank.write(update_vals)

                # Confirm the approval
                approval.action_confirm()

                # Set flag to indicate waiting on approval
                self.waiting_on_approval = True
                self.env.cr.commit()

                raise UserError(
                    f"Approval '{approval.name}' has been created. The approval process for updating Bank Accounts "
                    f"and/or Credit Limits has begun."
                )

        elif self.waiting_on_approval and self.env.context.get('origin') != 'approval.request':
            raise UserError("There is already an Approval for this Contact's Accounting Changes.")

        return super(ResPartner, self).write(vals)
