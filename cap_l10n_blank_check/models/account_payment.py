from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, ValidationError
from odoo.tools.misc import formatLang, format_date


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    

    def _check_build_page_info(self, i, p):
        '''
            *** WARNING *** This is a non supered override. This function is only used once in base code. 
            Since it has a nested function and makes reference to static file props (INV_LINES_PER_STUB) there isnt a great way to maintain inheritance
            Care was given to pull in all references to this method from base
            Perhaps one day this can be more override friendly
        '''
        multi_stub = self.company_id.account_check_printing_multi_stub
        INV_LINES_PER_STUB = self.get_inv_lines_per_stub()
        amount_discount = '-'
        amount_invoice = '-'
        liquidity_lines, counterpart_lines, writeoff_lines = self._seek_for_lines()
        if 'Early Payment Discount' in str(writeoff_lines.mapped('name')):
            amount_discount = formatLang(self.env, sum(writeoff_lines.mapped('balance')), currency_obj=self.currency_id) if i == 0 else 'VOID'
        if self.reconciled_bill_ids:
            amount_invoice = formatLang(self.env, sum(self.reconciled_bill_ids.mapped('amount_total')), currency_obj=self.currency_id) if i == 0 else 'VOID'
        return {
            'sequence_number': self.check_number,
            'manual_sequencing': self.journal_id.check_manual_sequencing,
            'date': format_date(self.env, self.date),
            'partner_id': self.partner_id,
            'partner_name': self.partner_id.name,
            'currency': self.currency_id,
            'state': self.state,
            'amount': formatLang(self.env, self.amount, currency_obj=self.currency_id) if i == 0 else 'VOID',
            'amount_in_word': self._check_fill_line(self.check_amount_in_words) if i == 0 else 'VOID',
            'memo': self.ref,
            'stub_cropped': not multi_stub and len(self.move_id._get_reconciled_invoices()) > INV_LINES_PER_STUB,
            # If the payment does not reference an invoice, there is no stub line to display
            'stub_lines': p,
            # From the l10n_ca_check_printing module
            'date_label': self.company_id.account_check_printing_date_label,
            'payment_date_canada': format_date(self.env, self.date, date_format='yyyy-MM-dd'),
            #Custom params added
            'micr_text': self.get_micr_font() if i == 0 else False,
            'amount_invoice': amount_invoice,
            'amount_discount' : amount_discount,
        }
    
    
    def _check_make_stub_pages(self):
        """ 
            *** WARNING *** This is a non supered override. This function is only used once in base code. 
            Since it has a nested function and makes reference to static file props (INV_LINES_PER_STUB) there isnt a great way to maintain inheritance
            Perhaps one day this can be more override friendly
            The original comment from base code is kept below.
        
            '''The stub is the summary of paid invoices. It may spill on several pages, in which case only the check on
            first page is valid. This function returns a list of stub lines per page.'''
        """
        INV_LINES_PER_STUB = self.get_inv_lines_per_stub()
        self.ensure_one()
        
        def prepare_vals(invoice, partials):
            number = ' - '.join([invoice.name, invoice.ref] if invoice.ref else [invoice.name])
            if invoice.is_outbound() or invoice.move_type == 'in_receipt':
                invoice_sign = 1
                partial_field = 'debit_amount_currency'
            else:
                invoice_sign = -1
                partial_field = 'credit_amount_currency'
            if invoice.currency_id.is_zero(invoice.amount_residual):
                amount_residual_str = '-'
            else:
                amount_residual_str = formatLang(self.env, invoice_sign * invoice.amount_residual, currency_obj=invoice.currency_id)
            discount_taken_lines = invoice.line_ids.filtered(lambda x: x.epd_taken)
            discount_amount = False
            paid_amount = formatLang(self.env, invoice_sign * sum(partials.mapped(partial_field)), currency_obj=self.currency_id)
            if discount_taken_lines:
                discount_amount = sum([ (invoice_sign * -1) * abs(x.balance - x.discount_balance) for x in discount_taken_lines ])
                if discount_amount:
                    original_amount = invoice_sign * sum(partials.mapped(partial_field))
                    paid_amount = formatLang(self.env, (original_amount + discount_amount), currency_obj=self.currency_id)
            return {
                'due_date': format_date(self.env, invoice.invoice_date_due),
                'number': number,
                'amount_total': formatLang(self.env, invoice_sign * invoice.amount_total, currency_obj=invoice.currency_id),
                'discount_taken': formatLang(self.env, discount_amount, currency_obj=invoice.currency_id) if discount_amount else '-',
                'amount_residual': amount_residual_str,
                'amount_paid': paid_amount ,
                'currency': invoice.currency_id,
            }

        # Decode the reconciliation to keep only invoices.
        term_lines = self.line_ids.filtered(lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))
        invoices = (term_lines.matched_debit_ids.debit_move_id.move_id + term_lines.matched_credit_ids.credit_move_id.move_id)\
            .filtered(lambda x: x.is_outbound() or x.move_type == 'in_receipt')
        invoices = invoices.sorted(lambda x: x.invoice_date_due or x.date)
        # Group partials by invoices.
        invoice_map = {invoice: self.env['account.partial.reconcile'] for invoice in invoices}
        for partial in term_lines.matched_debit_ids:
            invoice = partial.debit_move_id.move_id
            if invoice in invoice_map:
                invoice_map[invoice] |= partial
        for partial in term_lines.matched_credit_ids:
            invoice = partial.credit_move_id.move_id
            if invoice in invoice_map:
                invoice_map[invoice] |= partial
        # Prepare stub_lines.
        if 'out_refund' in invoices.mapped('move_type'):
            stub_lines = [{'header': True, 'name': "Bills"}]
            stub_lines += [prepare_vals(invoice, partials)
                           for invoice, partials in invoice_map.items()
                           if invoice.move_type == 'in_invoice']
            stub_lines += [{'header': True, 'name': "Refunds"}]
            stub_lines += [prepare_vals(invoice, partials)
                           for invoice, partials in invoice_map.items()
                           if invoice.move_type == 'out_refund']
        else:
            stub_lines = [prepare_vals(invoice, partials)
                          for invoice, partials in invoice_map.items()
                          if invoice.move_type in ('in_invoice', 'in_receipt')]
        # Crop the stub lines or split them on multiple pages
        if not self.company_id.account_check_printing_multi_stub:
            # If we need to crop the stub, leave place for an ellipsis line
            num_stub_lines = len(stub_lines) > INV_LINES_PER_STUB and INV_LINES_PER_STUB - 1 or INV_LINES_PER_STUB
            stub_pages = [stub_lines[:num_stub_lines]]
        else:
            stub_pages = []
            i = 0
            while i < len(stub_lines):
                # Make sure we don't start the credit section at the end of a page
                if len(stub_lines) >= i + INV_LINES_PER_STUB and stub_lines[i + INV_LINES_PER_STUB - 1].get('header'):
                    num_stub_lines = INV_LINES_PER_STUB - 1 or INV_LINES_PER_STUB
                else:
                    num_stub_lines = INV_LINES_PER_STUB
                stub_pages.append(stub_lines[i:i + num_stub_lines])
                i += num_stub_lines
        return stub_pages

    
    def get_micr_font(self):
        '''
            Generates the MICR line for the check using the MICR E-13B font standards.

            This function checks if the payment's journal is configured to use a blank check printing layout.
            If so, it constructs the MICR line using the journal's transit number, account number, and the payment's check number.

            Raises:
                ValidationError: If the journal's transit number, account number, or the payment's check number is not set.

            Returns:
                str: The MICR line formatted for printing.
                bool: False if the check layout is not one of the specified layouts.

            Example:
                >>> payment.get_micr_font()
                'A123456789A C000012345678C 1000123456C'
        '''
        self.ensure_one()
        check_layout = self.journal_id.company_id.account_check_printing_layout
        if str(check_layout) not in ['cap_l10n_blank_check.action_print_blank_check_top']:
            return False
        else:
            if not self.journal_id.check_transit_number and not self.journal_id.check_account_number and not self.check_number:
                raise ValidationError( _(f"To use this check layout the journal [{self.journal_id.name}] needs to have the 'Transit' and 'Account' numbers set and this payment needs a valid check number") )
            else:
                micr_text = f"A{self.journal_id.check_transit_number}A C{str(self.journal_id.check_account_number.replace('-','D')).zfill(12)}C {self.check_number}C"
                return micr_text
    
    def get_inv_lines_per_stub(self):
        '''
            Helper method to either return how many lines to fit on a check page
            18 is a safe amount to use with the custom blank check layout
            9 is the base amount to use if using the base check layouts
        '''
        check_layout = self.journal_id.company_id.account_check_printing_layout
        if str(check_layout) in ['cap_l10n_blank_check.action_print_blank_check_top']:
            return 18
        else:
            return 9