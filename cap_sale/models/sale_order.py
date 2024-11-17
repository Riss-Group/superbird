from odoo import fields, api, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _update_expected_revenue(self, opportunity, amount):
        """
            Helper function to assist in redefining an Opportunity's Expected Revenue
        """
        if opportunity:
            opportunity.expected_revenue += amount

    def _compute_order_revenue(self):
        """
            Helper function to assist in calculating a Sale Order's total
        """
        return sum(line.price_unit * line.product_uom_qty for line in self.order_line)

    @api.model
    def create(self, vals):
        sale_order = super(SaleOrder, self).create(vals)
        if sale_order.opportunity_id:
            self._update_expected_revenue(sale_order.opportunity_id, sale_order._compute_order_revenue())
        return sale_order

    def write(self, vals):
        for order in self:
            if order.opportunity_id:
                old_revenue = order._compute_order_revenue()

                result = super(SaleOrder, self).write(vals)

                new_revenue = order._compute_order_revenue()
                self._update_expected_revenue(order.opportunity_id, new_revenue - old_revenue)
            else:
                result = super(SaleOrder, self).write(vals)
        return result

    def unlink(self):
        for order in self:
            if order.opportunity_id:
                total_expected_revenue = sum(
                    line.price_unit * line.product_uom_qty
                    for order in order.opportunity_id.order_ids
                    if order.state != 'cancel'
                    for line in order.order_line
                )
                order.opportunity_id.expected_revenue = total_expected_revenue
        return super(SaleOrder, self).unlink()

    def action_cancel(self):
        for order in self:
            if order.opportunity_id and order.state != 'cancel':
                self._update_expected_revenue(order.opportunity_id, -order._compute_order_revenue())
        return super(SaleOrder, self).action_cancel()
