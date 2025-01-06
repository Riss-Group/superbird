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
    create_pdi_receipt = fields.Boolean(string="Create Receipt PDI")
    pdi_receipt_service_template_id = fields.Many2one('service.template', string='Service PDI Rcpt')
    create_pdi_delivery = fields.Boolean(string="Create Delivery PDI")
    pdi_delivery_service_template_id = fields.Many2one('service.template', string='Service PDI Del')
    available_vehicle_model_ids = fields.Many2many('fleet.vehicle.model', compute='_compute_available_vehicle_model_ids')
    options_package_ok = fields.Boolean(string="Options Package")
    package_service_template_id = fields.Many2one('service.template', string='Service Packages Template')


    @api.onchange('options_package_ok', 'sale_ok', 'detailed_type')
    def _onchange_options_sale(self):
        if self.detailed_type != 'service':
            self.options_package_ok = False
            self.package_service_template_id = False
        if not self.sale_ok:
            self.options_package_ok = False
        if not self.sale_ok or not self.options_package_ok:
            self.package_service_template_id = False
    
    @api.onchange('package_service_template_id')
    def _onchange_package_service_template_id(self):
        if self.package_service_template_id:
            service_total = sum(self.package_service_template_id.service_template_parts.mapped('est_subtotal'))
            parts_total = sum(self.package_service_template_id.service_template_service.mapped('est_subtotal'))
            self.list_price = service_total + parts_total

    @api.onchange('tracking', 'purchase_ok')
    def _onchange_tracking_purchase(self):
        if self.tracking != 'serial' or not self.purchase_ok:
            self.create_fleet_vehicle = False
            self.vehicle_make_id = False
            self.vehicle_model_id = False
            self.vehicle_year = False
            self.create_pdi_receipt = False
            self.pdi_receipt_service_template_id = False
            self.create_pdi_delivery = False
            self.pdi_delivery_service_template_id = False
    
    @api.onchange('create_fleet_vehicle')
    def _onchange_create_fleet_vehicle(self):
        if not self.create_fleet_vehicle:
            self.vehicle_make_id = False
            self.vehicle_model_id = False
            self.vehicle_year = False
    
    @api.onchange('create_pdi_receipt')
    def _onchange_create_pdi_receipt(self):
        if not self.create_pdi_receipt:
            self.pdi_receipt_service_template_id = False
    
    @api.onchange('create_pdi_delivery')
    def _onchange_create_pdi_delivery(self):
        if not self.create_pdi_delivery:
            self.pdi_delivery_service_template_id = False
    
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
        if ('options_package_ok' in vals or 'sale_ok' in vals or 'detailed_type' in vals) and not self.env.context.get('skip_onchange_options_sale'):
            for record in self:
                record.with_context(skip_onchange_options_sale=True)._onchange_options_sale()
        if 'package_service_template_id' in vals and not self.env.context.get('skip_onchange_package_service_template_id') :
            for record in self:
                record.with_context(skip_onchange_package_service_template_id=True)._onchange_package_service_template_id()
        return res
    
    @api.model_create_multi
    def create(self, vals):
        records = super().create(vals)
        for val in vals:
            if val.get('vehicle_year'):
                for record in records:
                    record.product_variant_ids._compute_sequence_code()
        return records