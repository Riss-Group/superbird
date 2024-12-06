from odoo import models, fields, api
from odoo.tools.float_utils import float_compare

class StockPutawayRule(models.Model):
    _inherit = 'stock.putaway.rule'

    use_of_location = fields.Selection(related='storage_category_id.use_of_location', string="Use of location", store=True)
    location_type = fields.Selection(related='storage_category_id.location_type', string="Location type", store=True)
    location_specification = fields.Selection(related='storage_category_id.location_specification', string="Location specification", store=True)
    same_velocity = fields.Boolean(string="Same velocity", compute="_compute_same_velocity", store=True)

    @api.depends('storage_category_id.velocity_id')
    def _compute_same_velocity(self):
        for record in self:
            record.same_velocity = bool(record.storage_category_id.velocity_id)

    #todo: call super and super only
    def _get_putaway_location(self, product, quantity=0, package=None, packaging=None, qty_by_location=None):

        package_type = self.env['stock.package.type']
        if package:
            package_type = package.package_type_id
        elif packaging:
            package_type = packaging.package_type_id

        checked_locations = set()
        for putaway_rule in self:
            location_out = putaway_rule.location_out_id
            child_locations = location_out.child_internal_location_ids

            if not putaway_rule.storage_category_id and not putaway_rule.use_of_location and not putaway_rule.location_type and not putaway_rule.location_specification and not putaway_rule.same_velocity:
                if location_out in checked_locations:
                    continue
                if location_out._check_can_be_used(product, quantity, package, qty_by_location[location_out.id]):
                    return location_out
                continue
            else:
                if putaway_rule.storage_category_id:
                    child_locations = child_locations.filtered(lambda loc: loc.storage_category_id == putaway_rule.storage_category_id)
                if putaway_rule.use_of_location:
                    child_locations = child_locations.filtered(lambda loc: loc.use_of_location == putaway_rule.use_of_location)
                if putaway_rule.location_type:
                    child_locations = child_locations.filtered(lambda loc: loc.location_type == putaway_rule.location_type)
                if putaway_rule.location_specification:
                    child_locations = child_locations.filtered(lambda loc: loc.location_specification == putaway_rule.location_specification)
                if putaway_rule.same_velocity:
                    child_locations = child_locations.filtered(lambda loc: loc.velocity_id == product.velocity_id)

            # check if already have the product/package type stored
            for location in child_locations:
                if location in checked_locations:
                    continue
                if package_type:
                    if location.quant_ids.filtered(lambda q: q.package_id and q.package_id.package_type_id == package_type):
                        if location._check_can_be_used(product, quantity, package=package, location_qty=qty_by_location[location.id]):
                            return location
                        else:
                            checked_locations.add(location)
                elif float_compare(qty_by_location[location.id], 0, precision_rounding=product.uom_id.rounding) > 0:
                    if location._check_can_be_used(product, quantity, location_qty=qty_by_location[location.id]):
                        return location
                    else:
                        checked_locations.add(location)

            # check locations with matched storage category
            for location in child_locations.filtered(lambda l: l.storage_category_id == putaway_rule.storage_category_id or not putaway_rule.storage_category_id):
                if location in checked_locations:
                    continue
                if location._check_can_be_used(product, quantity, package, qty_by_location[location.id]):
                    return location
                checked_locations.add(location)

        return None