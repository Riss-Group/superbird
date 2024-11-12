from odoo import  models, fields, api, _
from odoo.exceptions import UserError
from odoo.osv import expression
import logging 
logger = logging.getLogger()


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    

    fleet_vehicle_warranty_line = fields.One2many('fleet.vehicle.warranty.line', 'fleet_vehicle_id')
    stock_number = fields.Char(tracking=True)
    body_number = fields.Char(tracking=True)
    engine_number = fields.Char(string="Engine SN", tracking=True)
    transmission_number = fields.Char(string="Transmission SN", tracking=True)
    diesel_particulate_number = fields.Char(string="Diesel Particulate SN", tracking=True)
    cat_convert_number = fields.Char(string="Catalytic Converter SN", tracking=True)
    front_axle_number = fields.Char(string="Front Axle SN", tracking=True)
    rear_axle_number = fields.Char(string="Rear Axle SN", tracking=True)
    ignition_key_number = fields.Char(string="Ignition Key SN", tracking=True)
    product_template_variant_value_ids = fields.Many2many('product.template.attribute.value', string='Attributes', related='product_id.product_template_variant_value_ids')
    customer_id = fields.Many2one('res.partner', ondelete="restrict", tracking=True)
    customer_ref_num = fields.Char(tracking=True, string="Customer Reference")
    product_id = fields.Many2one('product.product', ondelete="restrict", tracking=True)
    sold_date = fields.Date(tracking=True)
    fleet_move_line_ids = fields.One2many('stock.move.line', 'fleet_vehicle_id')
    fleet_move_line_count = fields.Integer(compute='_compute_fleet_move_line_count')
    service_order_ids = fields.One2many('service.order', 'fleet_vehicle_id')
    service_order_ids_count = fields.Integer(compute='_compute_service_order_ids_count')
    is_bus_fleet = fields.Boolean(related='model_id.is_bus_fleet')


    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if operator != 'ilike' or (name or '').strip():
            domain = [
                '|', ('name', 'ilike', name),
                '|', ('brand_id.name', 'ilike', name),
                '|', ('vin_sn', 'ilike', name),
                '|', ('body_number', 'ilike', name),
                '|', ('stock_number', 'ilike', name),
                ('customer_ref_num', 'ilike', name)
            ]
        return self._search(domain, limit=limit, order=order)
    
    @api.depends('model_id.brand_id.name', 'model_id.name', 'body_number')
    def _compute_vehicle_name(self):
        for record in self:
            record.name = (record.model_id.brand_id.name or '') + '/' + (record.model_id.name or '') + '/' + (record.body_number or _('NA'))

    @api.depends('fleet_move_line_ids')
    def _compute_fleet_move_line_count(self):
        for record in self:
            record.fleet_move_line_count = len(record.fleet_move_line_ids)
        
    @api.depends('service_order_ids')
    def _compute_service_order_ids_count(self):
        for record in self:
            record.service_order_ids_count = len(record.service_order_ids)

    def action_fleet_move_lines(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fleet Moves',
            'view_mode': 'tree,form',
            'res_model': 'stock.move.line',
            'domain': [('id', 'in', self.fleet_move_line_ids.ids)]
        }
    
    def action_service_order_ids(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fleet Moves',
            'view_mode': 'tree,form',
            'res_model': 'stock.move.line',
            'domain': [('id', 'in', self.service_order_ids.ids)]
        }
