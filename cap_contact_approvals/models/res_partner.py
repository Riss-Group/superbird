from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    waiting_on_approval = fields.Boolean(string="Waiting on Approval")

    @api.model
    def create(self, vals):
        credit_limit = 0.0
        if 'credit_limit' in vals.keys() and vals['credit_limit'] != self.env['ir.property']._get('credit_limit', 'res.partner'):
            credit_limit = vals.get('credit_limit')
            vals['use_partner_credit_limit'] = False
            vals['credit_limit'] = self.env['ir.property']._get('credit_limit', 'res.partner')
        partner = super(ResPartner, self).create(vals)
        if credit_limit:
            approval = partner.create_approval_request()
            approval.credit_limit = credit_limit
            approval.credit_limits_changed = True
            # Confirm the approval
            approval.action_confirm()

            # Set flag to indicate waiting on approval
            partner.waiting_on_approval = True
            self.env.cr.commit()

            raise UserError(
                f"Approval '{approval.name}' has been created. The approval process for updating Bank Accounts "
                f"and/or Credit Limits has begun."
            )
        return partner

    def write(self, vals):
        bank_fields = {'bank_ids', 'acc_number', 'allow_payment', 'acc_holder_name'}
        credit_fields = {'credit_limit'}
        use_partner_credit_limit = {'use_partner_credit_limit'}
        # credit_fields = {}

        field_keys = set(bank_fields)
        val_keys = set(vals.keys())
        if 'use_partner_credit_limit' in val_keys and not vals['use_partner_credit_limit']:
            field_keys = set(field_keys | use_partner_credit_limit)

        if 'credit_limit' in val_keys and vals['credit_limit'] != self.env['ir.property']._get('credit_limit', 'res.partner'):
            field_keys = set(field_keys | credit_fields)

        if field_keys & val_keys and not any(partner.waiting_on_approval for partner in self):
            for partner in self.filtered(lambda p: not p.waiting_on_approval):
                approval = partner.create_approval_request()
                if bool(bank_fields & val_keys):
                    approval.bank_changed = True

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
                        existing_bank = self.env['res.partner.bank'].browse(bank_id)
                        if existing_bank:
                            existing_bank.write({'update_vals': update_vals, 'approval_id': approval.id, 'command': 1,})

                    elif command[0] == 2:  # DELETE
                        bank_id = command[1]
                        update_vals = {
                            'approval_id': approval.id,
                            'command': 2,
                        }
                        existing_bank = self.env['res.partner.bank'].browse(bank_id)
                        if existing_bank:
                            existing_bank.write(update_vals)
                if bool(credit_fields | use_partner_credit_limit & val_keys):
                    if 'credit_limit' in val_keys and vals.get('credit_limit') != self.env['ir.property']._get('credit_limit', 'res.partner'):
                        approval.credit_limit = vals['credit_limit']
                        approval.credit_limits_changed = True
                    elif 'use_partner_credit_limit' in val_keys and not vals.get('use_partner_credit_limit', False):
                        approval.credit_limit = self.env['ir.property']._get('credit_limit', 'res.partner')
                        approval.credit_limits_changed = True

                # Confirm the approval
                approval.action_confirm()

                # Set flag to indicate waiting on approval
                partner.waiting_on_approval = True
                self.env.cr.commit()

                raise UserError(
                    f"Approval '{approval.name}' has been created. The approval process for updating Bank Accounts "
                    f"and/or Credit Limits has begun."
                )

        elif all(partner.waiting_on_approval for partner in self) and self.env.context.get('origin') != 'approval.request':
            raise UserError("There is already an Approval for this Contact's Accounting Changes.")

        return super(ResPartner, self).write(vals)

    def create_approval_request(self):
        category = self.env['approval.category'].search([('sequence_code', '=', 'CCAI'),
                                                         ('company_id', '=', self.env.company.id)], limit=1)
        if not category:
            raise UserError("Approval category with code 'CCAI' is not defined.")
        approval_id = self.env['approval.request'].create({'date': fields.Datetime.now(),
                                                           'partner_id': self.id,
                                                           'category_id': category.id})
        return approval_id
