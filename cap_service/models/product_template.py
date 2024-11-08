from odoo import models, fields, api
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    

    def _get_years(self):
        current_year = fields.Date.today().year
        return [(str(year), str(year)) for year in range(current_year + 2, current_year - 26, -1)]


    create_fleet_vehicle = fields.Boolean('Create Fleet Vehicle', help="When checked, this product will automatically create a fleet vehicle record when receipted into inventory", )
    vehicle_year = fields.Selection(selection=_get_years, string="Year")
    vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand', string="Make")
    vehicle_model_id = fields.Many2one('fleet.vehicle.model', string="Model")
    available_vehicle_model_ids = fields.Many2many('fleet.vehicle.model', compute='_compute_available_vehicle_model_ids')


    @api.onchange('tracking', 'purchase_ok')
    def _onchange_tracking_purchase(self):
        if self.tracking != 'serial' or not self.purchase_ok:
            self.create_fleet_vehicle = False
            self.vehicle_make_id = False
            self.vehicle_model_id = False
            self.vehicle_year = False
    
    @api.onchange('create_fleet_vehicle')
    def _onchange_create_fleet_vehicle(self):
        if not self.create_fleet_vehicle:
            self.vehicle_make_id = False
            self.vehicle_model_id = False
            self.vehicle_year = False
    
    @api.onchange('vehicle_model_id')
    def _onchange_vehicle_model_id(self):
        if self.vehicle_model_id and not self.vehicle_make_id:
            self.vehicle_make_id = self.vehicle_model_id.brand_id
    
    @api.depends('vehicle_make_id')
    def _compute_available_vehicle_model_ids(self):
        for record in self:
            if not record.vehicle_model_id:
                record.available_vehicle_model_ids = self.env['fleet.vehicle.model'].search([('is_bus_fleet','=',True)])
            else:
                record.available_vehicle_model_ids = self.env['fleet.vehicle.model'].search([('id','in',record.vehicle_make_id.model_ids.ids)])
    
    def write(self, vals):
        res = super().write(vals)
        if vals.get('vehicle_year'):
            for record in self:
                record.product_variant_ids._compute_sequence_code()
        return res
    
    @api.model_create_multi
    def create(self, vals):
        records = super().create(vals)
        for val in vals:
            if val.get('vehicle_year'):
                for record in records:
                    record.product_variant_ids._compute_sequence_code()
        return records