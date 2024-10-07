from odoo import  models, fields, api, _
from odoo.exceptions import UserError
import logging
logger = logging.getLogger()


class ServiceOrder(models.Model):
    _name = 'service.order'   
    

    name = fields.Char(default=lambda self: '', copy=False)
    partner_id = fields.Many2one('res.partner')
    shipping_partner_id = fields.Many2one('res.partner')
    sale_order_id = fields.Many2one('sale.order')
    available_fleet_vehicle_ids = fields.Many2many('fleet.vehicle', compute='_compute_available_fleet_vehicle_ids', store=False)
    fleet_vehicle_id = fields.Many2one('fleet.vehicle')
    fleet_vehicle_make = fields.Many2one('fleet.vehicle.model.brand', related='fleet_vehicle_id.model_id.brand_id')
    fleet_vehicle_model = fields.Many2one('fleet.vehicle.model', related='fleet_vehicle_id.model_id')
    fleet_vehicle_year = fields.Char(related='fleet_vehicle_id.model_year')
    fleet_vehicle_vin_sn = fields.Char(related='fleet_vehicle_id.vin_sn')
    fleet_vehicle_stock_number = fields.Char(related='fleet_vehicle_id.stock_number')
    fleet_vehicle_body_number = fields.Char(related='fleet_vehicle_id.body_number')
    fleet_vehicle_ymm = fields.Char(compute='_compute_fleet_vehicle_ymm')
    fleet_vehicle_warranty_line = fields.One2many('fleet.vehicle.warranty.line',related='fleet_vehicle_id.fleet_vehicle_warranty_line')
    fleet_odometer_unit = fields.Selection(related='fleet_vehicle_id.odometer_unit')
    fleet_odometer_in = fields.Integer()
    fleet_odometer_out = fields.Integer()
    service_order_lines = fields.One2many('service.order.line', 'service_order_id')
    internal_memo = fields.Text()
    printed_memo = fields.Text()
    ref = fields.Char()
    total = fields.Float(compute="_compute_totals")
    customer_total = fields.Float(compute="_compute_totals")
    customer_parts_total = fields.Float(compute="_compute_totals")
    customer_service_total = fields.Float(compute="_compute_totals")
    warranty_total = fields.Float(compute="_compute_totals")
    warranty_parts_total = fields.Float(compute="_compute_totals")
    warranty_service_total = fields.Float(compute="_compute_totals")
    internal_total = fields.Float(compute='_compute_totals')
    internal_parts_total = fields.Float(compute='_compute_totals')
    internal_service_total = fields.Float(compute='_compute_totals')
    service_writer_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    payment_term_id = fields.Many2one('account.payment.term', compute='_compute_payment_term_id', store=True, readonly=False)
    start_date = fields.Datetime()
    end_date = fields.Datetime()
    task_ids = fields.Many2many('project.task', compute='_compute_task_ids')
    task_ids_count = fields.Integer(compute='_compute_task_ids')
    state = fields.Selection([
        ('draft','Draft'),
        ('quote','Quote'),
        ('confirmed','In Repair'),
        ('done','Done'),
        ],default='draft')


    @api.onchange('fleet_vehicle_id')
    def _onchange_fleet_vehicle_id(self):
        for record in self:
            record.fleet_odometer_in = record.fleet_vehicle_id.odometer
            record.fleet_odometer_unit = record.fleet_vehicle_id.odometer_unit
    
    @api.depends('partner_id')
    def _compute_payment_term_id(self):
        for order in self:
            order.payment_term_id = order.partner_id.property_payment_term_id
    
    @api.depends('fleet_vehicle_id')
    def _compute_fleet_vehicle_ymm(self):
        for record in self:
            record.fleet_vehicle_ymm = f"{record.fleet_vehicle_id.model_year or 'NA'}/{record.fleet_vehicle_make.name or 'NA'}/{record.fleet_vehicle_id.model_id.name or 'NA'}"
    
    @api.depends('partner_id')
    def _compute_available_fleet_vehicle_ids(self):
        for record in self:
            if record.partner_id:
                partner_domain = ['|', ('customer_id','=',record.partner_id.id), ('customer_id', 'child_of', [record.partner_id.id])]
                record.available_fleet_vehicle_ids = self.env['fleet.vehicle'].search(partner_domain)
            else:
                record.available_fleet_vehicle_ids = self.env['fleet.vehicle'].search([])

    def update_child_sequence(self):
        for parent in self:
            i = 1
            for service_line in parent.service_order_lines:
                service_line.update({'sequence': i})  
                i+= 1
    
    @api.depends('service_order_lines.task_id')
    def _compute_task_ids(self):
        for record in self:
            task_ids = record.service_order_lines.mapped('task_id')
            record.task_ids = task_ids
            record.task_ids_count = len(task_ids)
    
    @api.depends('service_order_lines.service_order_line_product_ids.quantity',
        'service_order_lines.service_order_line_product_ids.unit_price',
        'service_order_lines.service_order_line_service_ids.quantity',
        'service_order_lines.service_order_line_service_ids.unit_price',
    )
    def _compute_totals(self):
        for record in self:
            customer_parts = sum(x.quantity * x.unit_price for x in record.service_order_lines.filtered(lambda x: x.ttype == 'Customer').mapped('service_order_line_product_ids'))
            customer_service = sum(x.quantity * x.unit_price for x in record.service_order_lines.filtered(lambda x: x.ttype == 'Customer').mapped('service_order_line_service_ids'))
            warranty_parts = sum(x.quantity * x.unit_price for x in record.service_order_lines.filtered(lambda x: x.ttype == 'Warranty').mapped('service_order_line_product_ids'))
            warranty_service = sum(x.quantity * x.unit_price for x in record.service_order_lines.filtered(lambda x: x.ttype == 'Warranty').mapped('service_order_line_service_ids'))
            internal_parts = sum(x.quantity * x.unit_price for x in record.service_order_lines.filtered(lambda x: x.ttype == 'Internal').mapped('service_order_line_product_ids'))
            internal_service = sum(x.quantity * x.unit_price for x in record.service_order_lines.filtered(lambda x: x.ttype == 'Internal').mapped('service_order_line_service_ids'))
            record.customer_parts_total = customer_parts
            record.customer_service_total = customer_service
            record.customer_total = customer_parts + customer_service
            record.warranty_parts_total = warranty_parts
            record.warranty_service_total = warranty_service
            record.warranty_total = warranty_service + warranty_parts
            record.internal_parts_total = internal_parts
            record.internal_service_total = internal_service
            record.internal_total = internal_parts + internal_service
            record.total = customer_parts + customer_service + warranty_parts + warranty_service + internal_parts + internal_service
    
    def action_confirm(self):
        for record in self:
            record.sale_order_id = self.env['sale.order'].create(record._get_so_vals())
            record.state = 'quote' if record.state == 'draft' else record.state
    
    def action_open_portal(self):
        url = "https://vantage.blue-bird.com/Portal/Unit-Dashboard.aspx?search="
        if not url:
            raise UserError('Base URL is not defined in the settings')
        return {
        "type": "ir.actions.act_url",
        "url": f'{url}{self.fleet_vehicle_body_number}',
        "target": "new",  
        }

    def action_launch_repair(self):
        for record in self:
            for line in record.service_order_lines.filtered(lambda x: not x.task_id ):
                line.task_id = self.env['project.task'].create(record._get_task_vals(line))
            record.state = 'confirmed'
    
    def action_stat_button_task_ids(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tasks',
            'view_mode': 'kanban,tree,form',
            'res_model': 'project.task',
            'context' : {
                'search_default_group_by_stage_id': True
            },
            'domain': [('id', 'in', self.task_ids.ids)]
        }
    
    def button_add_from_template(self):
        '''
            Service ID is passed through context

            Returns:
                Window Action
        '''
        return {
            'name': 'Add Service Lines From Template',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'service.template.select',
            'context': {
                'default_service_order_id': self.id,
            },
            'target': 'new',
        }
    
    def _get_task_vals(self, line):
        self.ensure_one()
        task_vals = {
            'name': f"{self.name} - {line.name}",
            'description': line.name,
            'project_id': line.project_id.id,
            'planned_date_begin': self.start_date,
            'user_ids': False,
            'allocated_hours': line.hours
        }
        return task_vals

    def _get_so_vals(self):
        self.ensure_one()
        so_line_vals = []
        sequence=0
        service_line_counter = 1
        for line in self.service_order_lines:
            so_line_vals.append((0,0,{
                'display_type' : 'line_section',
                'name': f"{line.ttype} Service Issue #{service_line_counter}",
                'sequence':sequence,
                'service_order_line_id':line.id
            }))
            sequence += 1
            service_line_counter += 1
            so_line_vals.append((0,0,{
                'display_type' : 'line_note',
                'name': f"Description: {line.name or ''}",
                'display_type_ccc': 'name',
                'sequence':sequence,
                'service_order_line_id':line.id
            }))
            sequence += 1
            so_line_vals.append((0,0,{
                'display_type' : 'line_note',
                'name': f"Cause: {line.cause or ''}",
                'display_type_ccc': 'cause',
                'sequence':sequence,
                'service_order_line_id':line.id
            }))
            sequence += 1
            so_line_vals.append((0,0,{
                'display_type' : 'line_note',
                'name': f"Fix: {line.correction or ''}",
                'display_type_ccc': 'correction',
                'sequence':sequence,
                'service_order_line_id':line.id
            }))
            sequence += 1
            for service_line in line.service_order_line_service_ids:
                so_line_vals.append((0,0,{
                    'product_id': service_line.product_id.id,
                    'product_uom_qty': service_line.quantity,
                    'price_unit' : service_line.unit_price,
                    'sequence': sequence,
                    'service_order_line_id':line.id
                }))
                sequence += 1
            for product_line in line.service_order_line_product_ids:
                so_line_vals.append((0,0,{
                    'product_id': product_line.product_id.id,
                    'product_uom_qty': product_line.quantity,
                    'price_unit' : product_line.unit_price,
                    'sequence': sequence,
                    'service_order_line_id':line.id
                }))
                sequence += 1
        so_vals = {
            'partner_id' : self.partner_id.id,
            'client_order_ref': self.ref,
            'order_line': so_line_vals,
            'payment_term_id': self.payment_term_id.id,
            'user_id': self.service_writer_id.id,
            'service_order_id': self.id
        }
        if self.shipping_partner_id:
            so_vals['partner_shipping_id'] = self.shipping_partner_id
        return so_vals

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name', ''):
                vals['name'] = self.env['ir.sequence'].next_by_code('service.order')
        res = super().create(vals_list)
        for rec in res:
            rec.update_child_sequence()
        return res

    def write(self, vals):
        result = super().write(vals)
        for rec in self:
            rec.update_child_sequence()
        return result
