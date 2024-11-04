from odoo import fields, api, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        # Create the sale order record
        sale_order = super(SaleOrder, self).create(vals)
        
        # Check if there's an associated opportunity
        if sale_order.opportunity_id:
            # Calculate total expected revenue from all related sale orders, excluding canceled ones
            total_expected_revenue = sum(
                line.price_unit * line.product_uom_qty
                for order in sale_order.opportunity_id.order_ids
                if order.state != 'cancel'
                for line in order.order_line
            )
            
            # Update the opportunity's expected revenue
            sale_order.opportunity_id.expected_revenue = total_expected_revenue

        return sale_order

    def write(self, vals):
        # Check if there's an associated opportunity
        if self.opportunity_id:
            uom_qty_or_price_unit_changed = False

            # Detect changes in `product_uom_qty` or `price_unit` in order lines
            if 'order_line' in vals:
                for line_data in vals.get('order_line', []):
                    if line_data[0] == 1:  # Line update
                        line_id = line_data[1]
                        line_vals = line_data[2]

                        line = self.env['sale.order.line'].browse(line_id)
                        
                        # Check if `product_uom_qty` or `price_unit` was modified
                        if 'product_uom_qty' in line_vals and line_vals['product_uom_qty'] != line.product_uom_qty:
                            uom_qty_or_price_unit_changed = True
                        if 'price_unit' in line_vals and line_vals['price_unit'] != line.price_unit:
                            uom_qty_or_price_unit_changed = True

            # Apply the changes first
            result = super(SaleOrder, self).write(vals)

            # If any quantity or price was changed, update expected revenue on the opportunity
            if uom_qty_or_price_unit_changed:
                total_expected_revenue = sum(
                    line.price_unit * line.product_uom_qty
                    for order in self.opportunity_id.order_ids
                    if order.state != 'cancel'  # Exclude canceled orders
                    for line in order.order_line
                )

                self.opportunity_id.expected_revenue = total_expected_revenue
        else:
            # If no opportunity is associated, simply apply the changes
            result = super(SaleOrder, self).write(vals)

        return result
