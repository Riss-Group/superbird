from odoo import models, fields, api

class StockLocation(models.Model):
    _inherit = 'stock.location'

    @api.depends('name', 'location_id.complete_name', 'warehouse_id.location_name_separator')
    def _compute_complete_name(self):
        for location in self:
            if not (location.warehouse_id and location.location_id):
                super(StockLocation, location)._compute_complete_name()
            if location.location_id.parent_path.startswith(location.warehouse_id.lot_stock_id.parent_path) and location.location_id != location.warehouse_id.lot_stock_id:
                location.complete_name = ('%s%s%s' %
                                      (location.location_id.complete_name,
                                       location.warehouse_id.location_name_separator if location.warehouse_id.location_name_separator else '',
                                       location.name))
            else:
                location.complete_name = ('%s/%s' %
                                      (location.location_id.complete_name,
                                       location.name))