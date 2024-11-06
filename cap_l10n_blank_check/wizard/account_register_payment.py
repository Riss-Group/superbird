from odoo import fields, models, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'


    def _create_payment_vals_from_wizard(self, batch_result):
        '''
            Override of base create payment vals function
            If the payment made is consuming a discount the account move line should be tagged to indicate as such
        '''
        res = super()._create_payment_vals_from_wizard( batch_result=batch_result)
        epd_taken_list = []
        if self.payment_difference_handling == 'reconcile':
            if self.early_payment_discount_mode:
                for aml in batch_result['lines']:
                    if aml.move_id._is_eligible_for_early_payment_discount(self.currency_id, self.payment_date):
                        epd_taken_list.append(aml.id)
                if epd_taken_list:
                    self.env['account.move.line'].sudo().browse(epd_taken_list).write({'epd_taken':True})
        return res