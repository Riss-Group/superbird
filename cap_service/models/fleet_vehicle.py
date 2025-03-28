from odoo import  models, fields, api, _
from odoo.exceptions import UserError
from odoo.osv import expression
import logging 
logger = logging.getLogger()


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    

    fleet_vehicle_warranty_line = fields.One2many('fleet.vehicle.warranty.line', 'fleet_vehicle_id')
    stock_number = fields.Char(tracking=True, copy=False)
    body_number = fields.Char(tracking=True, copy=False)
    engine_number = fields.Char(string="Engine SN", tracking=True, copy=False)
    transmission_number = fields.Char(string="Transmission SN", tracking=True, copy=False)
    diesel_particulate_number = fields.Char(string="Diesel Particulate SN", tracking=True, copy=False)
    cat_convert_number = fields.Char(string="Catalytic Converter SN", tracking=True, copy=False)
    front_axle_number = fields.Char(string="Front Axle SN", tracking=True, copy=False)
    rear_axle_number = fields.Char(string="Rear Axle SN", tracking=True, copy=False)
    ignition_key_number = fields.Char(string="Ignition Key SN", tracking=True, copy=False)
    product_template_variant_value_ids = fields.Many2many('product.template.attribute.value', string='Attributes', related='product_id.product_template_variant_value_ids')
    customer_id = fields.Many2one('res.partner', ondelete="restrict", tracking=True)
    customer_ref_num = fields.Char(tracking=True, string="Customer Reference", copy=False)
    product_id = fields.Many2one('product.product', ondelete="restrict", tracking=True, copy=False)
    sold_date = fields.Date(tracking=True, copy=False)
    order_date = fields.Datetime(string="Order Date", tracking=True, copy=False)
    fleet_move_line_ids = fields.One2many('stock.move.line', 'fleet_vehicle_id')
    fleet_move_line_count = fields.Integer(compute='_compute_fleet_move_line_count')
    service_order_ids = fields.One2many('service.order', 'fleet_vehicle_id')
    service_order_ids_count = fields.Integer(compute='_compute_service_order_ids_count')
    service_order_worksheet_count = fields.Integer(compute='_compute_service_order_ids_count')
    is_bus_fleet = fields.Boolean(related='model_id.is_bus_fleet')
    active_demo_unit = fields.Boolean(tracking=True, copy=False)
    was_demo_unit = fields.Boolean(tracking=True, copy=False)
    rental_sale_line_ids = fields.One2many('sale.order.line', 'fleet_vehicle_rental_id')
    rental_sign_request_ids = fields.Many2many('sign.request', compute='compute_rental_sign_request_ids')
    rental_sign_request_count = fields.Integer(compute='compute_rental_sign_request_ids')
    has_outgoing_pdi = fields.Boolean( copy=False)
    has_outgoing_package_service = fields.Boolean(copy=False)
    has_incoming_pdi = fields.Boolean(copy=False)
    vin_sn = fields.Char(string="VIN Number", copy=False)
    ack_file =fields.Binary(string="Acknowledgement PDF", copy=False)
    ack_received = fields.Boolean(store=True, string="Acknowledgement Received", compute='_compute_ack_received')


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
            record.service_order_worksheet_count = sum(record.service_order_ids.mapped('worksheet_references_count'))
    
    @api.depends('rental_sale_line_ids')
    def compute_rental_sign_request_ids(self):
        for record in self:
            sign_ids = record.rental_sale_line_ids.order_id.sign_request_ids
            record.rental_sign_request_ids = sign_ids.ids
            record.rental_sign_request_count = len(sign_ids)
    
    @api.depends('ack_file')
    def _compute_ack_received(self):
        for record in self:
            record.ack_received = record.ack_file

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
            'name': 'Service Orders',
            'view_mode': 'tree,form',
            'res_model': 'service.order',
            'domain': [('id', 'in', self.service_order_ids.ids)]
        }
    
    def action_view_worksheets(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Worksheets'),
            'view_mode': 'tree',
            'res_model': 'service.order.worksheets',
            'context': {'service_order_ids': self.service_order_ids.ids},
            'target': 'current',
        }
    
    def action_fleet_ack(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Fleet Acknowledgement'),
            'view_mode': 'form',
            'res_model': 'fleet.ack',
            'context': {'default_fleet_vehicle_ids': self.ids},
            'target': 'new',
        }
    
    def action_rental_sign_request_ids(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sign.sign_request_action")
        action['domain'] = [('id','in',self.rental_sign_request_ids.ids)]
        return action
    
    @api.onchange('active_demo_unit')
    def _onchange_active_demo_unit(self):
        if self.active_demo_unit:
            self.was_demo_unit = True
            return {
                'warning': {
                    'title': "Permanent Action Warning",
                    'message': (
                        "Marking this unit as an active demo unit is permanent and cannot be undone. Proceed with caution!"
                    ),
                }}
    
    def _synchronize_product_fields(self):
        """
        Synchronize fields from the product to the fleet vehicle, particularly fuel type,
        and other related fields.

        The method uses a mapping to determine the fuel type based on a mapped attribute value.
        """
        self.ensure_one()
        fuel_mapping = {
            'D': 'diesel',
            'EV': 'electric',
            'G': 'gasoline',
            'P': 'lpg',
        }

        vals = {}
        fuel_attribute = self.product_template_variant_value_ids.filtered(lambda x: x.attribute_id.name.lower() == 'fuel')
        if fuel_attribute:
            fuel_type = fuel_mapping.get(fuel_attribute.name, None)
            if fuel_type:
                vals['fuel_type'] = fuel_type
        cap_attribute = self.product_template_variant_value_ids.filtered(lambda x: x.attribute_id.is_cap)
        if cap_attribute:
            try:
                seats = int(cap_attribute.name)
                vals['seats'] = seats
            except (ValueError, TypeError):
                logger.warning(f"Could not convert seating capacity '{cap_attribute.name}' to an integer for fleet id {self.id}.")
        vals['model_year'] = self.product_id.vehicle_year
        if vals:
            self.write(vals)
    
    def _create_fleet_pdi(self, direction=None):
        if not direction:
            return
        for record in self:
            template_ids = record.product_id.pdi_receipt_service_template_id if direction == 'in' else record.product_id.pdi_delivery_service_template_id
            create_service = False
            if direction == 'in' and record.product_id.create_pdi_receipt and not record.has_incoming_pdi:
                create_service = True
                record.has_incoming_pdi = True
            elif direction == 'out' and record.product_id.create_pdi_delivery and not record.has_outgoing_pdi:
                create_service = True
                record.has_outgoing_pdi = True
            if create_service:                
                company_id = self.company_id.service_branch_id
                service_vals = {
                    'end_date' : record.order_date,
                    'partner_id' : record.customer_id.id,
                    'fleet_vehicle_id' : record.id,
                    'company_id':company_id.id
                }
                if fields.Datetime.now() > record.order_date:
                    service_vals.update({'start_date': record.order_date})
                service_order_id = self.env['service.order'].create(service_vals)
                service_order_id.message_post(body="Service Order auto-generated for incoming PDI Receipt", subtype_xmlid='mail.mt_note')
                service_order_id._onchange_fleet_vehicle_id()
                service_template_select = self.env['service.template.select'].create({
                    'service_order_id': service_order_id.id,
                    'service_template': [(6,0,template_ids.ids)]
                })
                service_template_select.button_save()
                service_order_id.action_upsert_so()
                service_order_id.action_create_tasks()

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val.get('active_demo_unit'):
                val['was_demo_unit'] = True
        records = super().create(vals)
        for record in records:
            if not self.env.context.get('no_sync'):
                record.with_context(no_sync=True)._synchronize_product_fields()
        return records

    def write(self, vals):
        if 'active_demo_unit' in vals and vals['active_demo_unit']:
            vals['was_demo_unit'] = True
        if 'was_demo_unit' in vals and not vals['was_demo_unit']:
            raise UserError("The field 'Was Demo Unit' cannot be unset once it has been marked as True.")
        res = super().write(vals)
        if 'product_id' in vals and not self.env.context.get('no_sync'):
            for record in self:
                record.with_context(no_sync=True)._synchronize_product_fields()
        return res