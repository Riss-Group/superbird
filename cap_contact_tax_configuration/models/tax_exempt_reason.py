from odoo import fields, models


class TaxExemptReason(models.Model):
    _name = 'tax.exempt.reason'

    name = fields.Text('Reason')
