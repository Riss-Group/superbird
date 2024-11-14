from odoo import models, fields, api

class StockStorageCategory(models.Model):
    _inherit = 'stock.storage.category'

    use_of_location = fields.Selection([
        ('O', 'Overstock (O)'),
        ('P', 'Picking (P)'),
    ], string="Use of location", default="P", required=True)

    pallets = fields.Boolean(string="Pallets (Y/N)", default=True, required=True)

    location_type = fields.Selection([
        ('F', 'Floor (F)'),
        ('R', 'Rack (R)'),
        ('S', 'Shelf (S)'),
        ('VR', 'Vertical rack (VR)'),
        ('W', 'Wall (W)'),
        ('C', 'Cantilever (C)'),
    ], string="Location type", required=True)

    location_specification = fields.Selection([
        ('G', 'Glass (G)'),
        ('E', 'Exhaust (E)'),
        ('O', 'Oversize (O)'),
        ('S', 'Sprinkler (S)'),
        ('F', 'Flammable (F)'),
        ('FS', 'Foam w sprinkler (FS)'),
        ('H', 'Hooked (H)'),
        ('NS', 'No specification (NS)'),
    ], string="Location specification", required=True)

    velocity_id = fields.Many2one('stock.storage.velocity', string="Velocity")
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")

    length = fields.Float(string="Length")
    depth = fields.Float(string="Depth")
    height = fields.Float(string="Height")
    volume = fields.Float(string="Volume")
    volume_uom_name = fields.Char(string='Volume unit of measure label', compute='_compute_volume_uom_name')
    length_uom_name = fields.Char(string='Length unit of measure label', compute='_compute_length_uom_name')


    name = fields.Char(compute="_compute_name", store=True)

    @api.depends('use_of_location', 'pallets', 'location_type', 'location_specification', 'velocity_id')
    def _compute_name(self):
        for record in self:
            record.name = '{}{}{}{}{}'.format(
                record.use_of_location or '',
                'Y' if record.pallets else 'N',
                record.location_type or '',
                record.location_specification or '',
                record.velocity_id.name if record.velocity_id else ''
            )
    def _compute_volume_uom_name(self):
        self.volume_uom_name = self.env['product.template']._get_volume_uom_name_from_ir_config_parameter()

    def _compute_length_uom_name(self):
        self.length_uom_name = self.env['product.template']._get_length_uom_name_from_ir_config_parameter()


class StockStorageVelocity(models.Model):
    _name = 'stock.storage.velocity'
    _description = 'Stock Storage Velocity'

    name = fields.Char(string='Velocity')