from odoo import _, api, fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _get_batch_available_journals(self, batch_result):
        res = super(AccountPaymentRegister, self)._get_batch_available_journals(batch_result)
        res = res.filtered(lambda x: not x.employee_id)
        return res
