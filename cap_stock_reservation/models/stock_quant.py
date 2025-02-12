from odoo import _, api, fields, models
from odoo.osv import expression



class StockQuant(models.Model):
    _inherit = "stock.quant"

    location_removal_priority = fields.Integer(string="Removal Priority", compute="_compute_location_removal_priority",
                                               store=True)  # NOTE: This field is only stored to allow sorting by removal_priority in the tree view


    @api.depends('location_id', 'location_id.removal_priority')
    def _compute_location_removal_priority(self):
        """Computes field 'location_removal_priority'. """

        for rec in self:
            rec.location_removal_priority = rec.location_id.removal_priority

    def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False, qty=0):
        res = super(StockQuant, self)._gather(product_id, location_id, lot_id, package_id, owner_id, strict, qty)

        # Sort by location_removal_priority first
        sorted_res = res.sorted(lambda x: x.location_removal_priority)

        # Check if the first quant has quantity < qty
        if sorted_res and sorted_res[0].quantity < qty:
            # Look for a quant with exact quantity == qty
            exact_match = sorted_res.filtered(lambda x: x.quantity == qty)

            if exact_match:
                # Move the first exact match to the front
                first_match = exact_match[0]
                sorted_res = sorted_res - first_match  # Remove it from the list
                sorted_res = first_match + sorted_res  # Insert it at the front

        return sorted_res


class StockLocation(models.Model):

    _inherit = "stock.location"

    removal_priority = fields.Integer(default=99)