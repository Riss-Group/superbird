from odoo import models, fields
from odoo.tools import float_round
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def button_admin_distribution(self):
        """
        Replace journal items with redistributed credits and debits based on
        account distribution lines.
        """
        for move in self:
            new_lines = []
            lines_to_remove = []

            for line in move.line_ids:
                has_gl_distribution_lines = bool(line.account_id.account_distribution_lines)
                if has_gl_distribution_lines:
                    lines_to_remove.append(line)

                    original_debit = line.debit
                    original_credit = line.credit
                    partner = line.partner_id
                    name = line.name

                    total_distributed_debit = 0
                    total_distributed_credit = 0

                    for dist_idx, dist_line in enumerate(line.account_id.account_distribution_lines):
                        distributed_debit = float_round(original_debit * (dist_line.percent_distribution / 100), precision_digits=2)
                        distributed_credit = float_round(original_credit * (dist_line.percent_distribution / 100), precision_digits=2)

                        total_distributed_debit += distributed_debit
                        total_distributed_credit += distributed_credit

                        new_line = {
                            'account_id': dist_line.account_distribution_id.id,
                            'debit': distributed_debit,
                            'credit': distributed_credit,
                            'partner_id': partner.id,
                            'name': f"(Distributed to {dist_line.account_distribution_id.name})",
                        }

                        if dist_idx == len(line.account_id.account_distribution_lines) - 1:
                            if original_debit > 0:
                                new_line['debit'] += float_round(original_debit - total_distributed_debit, precision_digits=2)
                            if original_credit > 0:
                                new_line['credit'] += float_round(original_credit - total_distributed_credit, precision_digits=2)

                        new_lines.append((0, 0, new_line))

            move.write({
                'line_ids': [(2, line.id, 0) for line in lines_to_remove] + new_lines
            })

    def button_expense_distribution(self):
        """
        Replace journal items with redistributed credits and debits based on
        account distribution lines.
        """
        for move in self:
            new_lines = []
            lines_to_remove = []

            for line in move.line_ids:
                has_gl_distribution_lines = bool(line.account_id.account_expense_distribution_lines)
                if has_gl_distribution_lines:
                    lines_to_remove.append(line)

                    original_debit = line.debit
                    original_credit = line.credit
                    partner = line.partner_id
                    name = line.name

                    total_distributed_debit = 0
                    total_distributed_credit = 0

                    for dist_idx, dist_line in enumerate(line.account_id.account_expense_distribution_lines):
                        distributed_debit = float_round(original_debit * (dist_line.percent_distribution / 100), precision_digits=2)
                        distributed_credit = float_round(original_credit * (dist_line.percent_distribution / 100), precision_digits=2)

                        total_distributed_debit += distributed_debit
                        total_distributed_credit += distributed_credit

                        new_line = {
                            'account_id': dist_line.account_distribution_id.id,
                            'debit': distributed_debit,
                            'credit': distributed_credit,
                            'partner_id': partner.id,
                            'name': f"(Distributed to {dist_line.account_distribution_id.name})",
                        }

                        if dist_idx == len(line.account_id.account_expense_distribution_lines) - 1:
                            if original_debit > 0:
                                new_line['debit'] += float_round(original_debit - total_distributed_debit, precision_digits=2)
                            if original_credit > 0:
                                new_line['credit'] += float_round(original_credit - total_distributed_credit, precision_digits=2)

                        new_lines.append((0, 0, new_line))

            move.write({
                'line_ids': [(2, line.id, 0) for line in lines_to_remove] + new_lines
            })
