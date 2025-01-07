from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    check_transit_number = fields.Char()
    check_account_number = fields.Char()

    @api.constrains('check_transit_number', 'check_account_number')
    def _check_numeric_and_dash(self):
        """
        Ensures that the 'check_transit_number' and 'check_account_number' fields
        only contain integers or dashes.
        """
        pattern = re.compile(r'^[0-9\-]*$')
        for record in self:
            if record.check_transit_number and not pattern.match(record.check_transit_number):
                raise ValidationError("The Transit Number must contain only digits and dashes.")
            if record.check_account_number and not pattern.match(record.check_account_number):
                raise ValidationError("The Account Number must contain only digits and dashes.")