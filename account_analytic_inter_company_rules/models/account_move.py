from odoo import models, fields, _


class AccountMove(models.Model):
    _inherit = "account.move"

    auto_split = fields.Boolean(
        string="Auto Split Document", copy=False, default=False
    )
    auto_split_invoice_id = fields.Many2one(
        "account.move", string="Split Invoice", readonly=True, copy=False
    )
    origin_partner_id = fields.Many2one(
        "res.partner",
        string="Original Partner",
        compute="_compute_origin_partner_id",
        help="Customer/Vendor of the original invoice/bill",
    )

    def _compute_origin_partner_id(self):
        """
        Compute the origin partner ID for each account move record.
        """
        for move in self:
            origin_partner_id = (
                move.auto_split_invoice_id.partner_id.id
                if move.auto_split_invoice_id
                else False
            )
            if not origin_partner_id and move.auto_generated:
                # sudo() is used to bypass access rights
                auto_invoice = move.sudo().auto_invoice_id
                if (
                    auto_invoice
                    and auto_invoice.auto_split
                    and auto_invoice.auto_split_invoice_id
                ):
                    origin_partner_id = (
                        auto_invoice.auto_split_invoice_id.partner_id.id
                    )
            move.origin_partner_id = origin_partner_id

    def _inter_company_create_invoices(self):
        return super(
            AccountMove,
            self.filtered(
                lambda move: move.auto_split and move.auto_split_invoice_id
            ),
        )._inter_company_create_invoices()

    def _post(self, soft=True):
        posted = super()._post(soft)

        inverse_types = {
            "in_invoice": "out_invoice",
            "in_refund": "out_refund",
            "out_invoice": "in_invoice",
            "out_refund": "in_refund",
        }

        company_obj = self.env["res.company"]
        move_obj = moves = self.env["account.move"]
        analytic_account_obj = self.env["account.analytic.account"]

        for inv in posted.filtered(lambda inv: not inv.auto_split):
            for line in inv.invoice_line_ids.filtered(
                lambda line: line.analytic_distribution
            ):
                account_ids = [
                    int(account_id)
                    for account_id in line.analytic_distribution or {}
                ]
                if account_ids:
                    analytic_account_ids = analytic_account_obj.browse(
                        account_ids
                    )
                    interco_analytic_account_ids = analytic_account_ids.filtered(
                        lambda analytic_account: analytic_account.automate_interco_invoice
                    )
                    interco_partner_ids = interco_analytic_account_ids.mapped(
                        "interco_partner_id"
                    )
                    for interco_partner in interco_partner_ids:
                        company = company_obj._find_company_from_partner(
                            interco_partner.id
                        )
                        if (
                            company == inv.company_id
                            or inv.move_type not in inverse_types
                        ):
                            continue
                        invoice_vals = inv._analytic_prepare_invoice_data(
                            inverse_types[inv.move_type],
                            interco_partner=interco_partner,
                        )
                        invoice_vals["invoice_line_ids"] = []
                        interco_partner_analytic_account = interco_analytic_account_ids.filtered(
                            lambda analytic_account: analytic_account.interco_partner_id
                            == interco_partner
                        )
                        line_vals = line._analytic_prepare_invoice_line_data(
                            interco_partner_analytic_account,
                            interco_partner.property_account_position_id,
                        )
                        if line_vals["price_unit"] < 0:
                            if invoice_vals["move_type"] == "in_invoice":
                                invoice_vals["move_type"] = "in_refund"
                            elif invoice_vals["move_type"] == "out_invoice":
                                invoice_vals["move_type"] = "out_refund"
                            line_vals["price_unit"] = abs(
                                line_vals["price_unit"]
                            )
                        invoice_vals["invoice_line_ids"].append(
                            (
                                0,
                                0,
                                line_vals,
                            )
                        )
                        move = move_obj.create(invoice_vals)
                        moves |= move

        if moves:
            moves._post()

        return posted

    def _analytic_prepare_invoice_data(self, move_type, interco_partner):
        self.ensure_one()

        return {
            "move_type": move_type,
            "ref": self.ref,
            "partner_id": interco_partner.id,
            "currency_id": self.currency_id.id,
            "auto_split": True,
            "auto_split_invoice_id": self.id,
            "invoice_date": self.invoice_date,
            "invoice_date_due": self.invoice_date_due,
            "payment_reference": self.payment_reference,
            "fiscal_position_id": interco_partner.with_company(
                self.company_id
            ).property_account_position_id.id,
            "invoice_origin": _("%s Invoice: %s") % (
                self.company_id.name,
                self.name,
            ),
            "company_id": self.company_id.id,
        }


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    origin_analytic_move_line_id = fields.Many2one(
        "account.move.line", string="Origin Analytic Move Line"
    )

    def _analytic_prepare_invoice_line_data(
        self, interco_partner_analytic_account, fiscal_position_id
    ):
        self.ensure_one()

        interco_percents = sum(
            [
                self.analytic_distribution.get(str(line_analytic.id))
                for line_analytic in interco_partner_analytic_account
            ]
        )
        analytic_distribution = {
            str(account_id): (
                self.analytic_distribution[str(account_id)]
                * 100
                / interco_percents
            )
            for account_id in interco_partner_analytic_account.ids
        }
        account_id = self.company_id.account_interco_revenue_account_id
        if fiscal_position_id:
            account_id = fiscal_position_id.map_account(
                self.env["account.account"].browse(account_id.id)
            )

        vals = {
            "display_type": self.display_type,
            "sequence": self.sequence,
            "name": self.name,
            "product_id": self.product_id.id,
            "product_uom_id": self.product_uom_id.id,
            "quantity": self.quantity,
            "discount": self.discount,
            "price_unit": self.price_unit * interco_percents / 100,
            "analytic_distribution": analytic_distribution,
            "account_id": account_id.id or self.account_id.id,
            "origin_analytic_move_line_id": self.id,
        }

        return vals

    def _inter_company_prepare_invoice_line_data(self):
        """
        Inherit this method to flow the account from the original invoice
        to the new invoices created for the others companies.
        """
        vals = super(
            AccountMoveLine, self
        )._inter_company_prepare_invoice_line_data()
        if self.origin_analytic_move_line_id:
            company_b = self.env["res.company"]._find_company_from_partner(
                self.move_id.partner_id.id
            )
            origin_account = self.origin_analytic_move_line_id.account_id
            account = (
                self.env["account.account"]
                .with_company(company_b)
                .search(
                    [
                        ("code", "=", origin_account.code),
                        ("company_id", "=", company_b.id),
                    ],
                    limit=1,
                )
            )
            if account:
                vals["account_id"] = account.id
        return vals
