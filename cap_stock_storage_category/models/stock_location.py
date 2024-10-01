from odoo import models, fields, api

class StockLocation(models.Model):
    _inherit = 'stock.location'

    use_of_location = fields.Selection(related='storage_category_id.use_of_location', string="Use of location", store=True)
    location_type = fields.Selection(related='storage_category_id.location_type', string="Location type", store=True)
    location_specification = fields.Selection(related='storage_category_id.location_specification', string="Location specification", store=True)
    velocity_id = fields.Many2one('stock.storage.velocity', related='storage_category_id.velocity_id', string="Velocity", store=True)