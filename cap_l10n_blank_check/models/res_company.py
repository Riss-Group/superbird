from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    account_check_printing_layout = fields.Selection(selection_add=[('cap_l10n_blank_check.action_print_blank_check_top', 'Print Blank Check (Top)'),], 
        ondelete={'cap_l10n_blank_check.action_print_blank_check_top': 'set default',})
