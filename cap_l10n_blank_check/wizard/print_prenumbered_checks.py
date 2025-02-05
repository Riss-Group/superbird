from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PrintPreNumberedChecks(models.TransientModel):
    _inherit = 'print.prenumbered.checks'

    def print_checks(self):
        check_number = int(self.next_check_number)
        number_len = len(self.next_check_number or "")
        payments = self.env['account.payment'].browse(self.env.context['payment_ids'])

        # Post all draft payments
        payments.filtered(lambda r: r.state == 'draft').action_post()

        # Update payments that are posted and not marked as "move sent"
        payments.filtered(lambda r: r.state == 'posted' and not r.is_move_sent).write({'is_move_sent': True})

        # Assign check numbers to each payment
        for payment in payments:
            payment.check_number = '%0{}d'.format(number_len) % check_number
            check_number += 1

        # Call the do_print_checks method for payments
        checks_action = payments.do_print_checks()

        # Ensure checks_action is not None before trying to update it
        if checks_action:
            checks_action.update({'close_on_report_download': True})
            # Return the checks_action to trigger the download
            return checks_action
        else:
            raise UserError(
                _("An error occurred while generating the checks. Please check the configuration and try again."))
