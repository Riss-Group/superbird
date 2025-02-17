from odoo import _, api, fields, models
from odoo.osv import expression



class StockQuant(models.Model):
    _inherit = "stock.quant"

    location_usage = fields.Selection(
        selection=[("picking", "P"), ("overstock", "O")],
        string="Removal Priority", compute="_compute_location_removal_priority",
                                               store=True)  # NOTE: This field is only stored to allow sorting by removal_priority in the tree view


    @api.depends('location_id', 'location_id.location_usage')
    def _compute_location_removal_priority(self):
        """Computes field 'location_removal_priority'. """

        for rec in self:
            rec.location_usage = rec.location_id.location_usage

    def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False, qty=0):
        res = super(StockQuant, self)._gather(product_id, location_id, lot_id, package_id, owner_id, strict, qty)

        # Define sorting order for location_usage
        usage_priority = {"picking": 0, "overstock": 1}  # Lower value means higher priority

        # Sort by location_usage first (picking -> overstock)
        sorted_res = res.sorted(
            lambda x: usage_priority.get(x.location_id.location_usage, 2))  # Default priority is lowest if not found

        # Check if the first quant has quantity < qty
        if sorted_res and sorted_res[0].quantity < qty:
            # Look for a quant with exact quantity >= qty
            exact_match = sorted_res.filtered(lambda x: x.quantity >= qty)

            if exact_match:
                # Move the first exact match to the front
                first_match = exact_match[0]
                sorted_res = sorted_res - first_match
                sorted_res = first_match + sorted_res

        return sorted_res


class StockLocation(models.Model):

    _inherit = "stock.location"

    location_usage = fields.Selection(
        selection=[("picking", "P"), ("overstock", "O")], default="picking",
        string="Location Usage")