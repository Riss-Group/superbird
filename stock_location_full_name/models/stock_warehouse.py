from odoo import models, fields

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    location_name_separator = fields.Char(string='Location Name Separator', default='/')