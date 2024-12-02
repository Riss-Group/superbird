from odoo import models, fields, api
from odoo.osv.expression import OR, AND
import logging
logger = logging.getLogger()



class QualityPoint(models.Model):
    _inherit = "quality.point"


    dest_location_id = fields.Many2one('stock.location')
    source_location_id = fields.Many2one('stock.location')


    @api.model
    def _get_domain(self, product_ids, picking_type_id, measure_on='product', dest_location_id=False, source_location_id=False):
        """
        Override to update the domain with additional conditions for destination/source locations.
        """
        domain = super()._get_domain(product_ids, picking_type_id, measure_on)
        if dest_location_id or source_location_id:
            location_conditions = []
            if dest_location_id:
                location_conditions.append(('dest_location_id', '=', dest_location_id.id))
            if source_location_id:
                location_conditions.append(('source_location_id', '=', source_location_id.id))
            domain = [d for d in domain if not d[0] == 'picking_type_ids']
            domain = AND([domain, location_conditions])
        else:
            location_conditions = [
                ('dest_location_id', '=', False),
                ('source_location_id', '=', False),
            ]
            domain = AND([domain, location_conditions])
        return domain

    def write(self, vals):
        """
        Override the write method to reset source_location_id and dest_location_id
        if measure_on is changed and not equal to 'operation'.
        """
        if 'measure_on' in vals and vals['measure_on'] != 'operation':
            vals.update({
                'source_location_id': False,
                'dest_location_id': False,
            })
        return super().write(vals)