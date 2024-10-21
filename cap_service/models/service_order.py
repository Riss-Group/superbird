from odoo import  models, fields, api, _, Command
from odoo.exceptions import UserError
import logging
logger = logging.getLogger()


class ServiceOrder(models.Model):
    _name = 'service.order' 
    _description = "Service Order"  
    

    name = fields.Char(default=lambda self: '', copy=False)
    partner_id = fields.Many2one('res.partner')
    service_order_lines = fields.One2many('service.order.line', 'service_order_id', )
    warranty_partner_id = fields.Many2one('res.partner')
    shipping_partner_id = fields.Many2one('res.partner')
    seperate_warranty_docs = fields.Boolean(compute='_compute_seperate_warranty_docs')
    sale_order_ids = fields.One2many('sale.order', 'service_order_id')
    sale_order_count = fields.Integer(compute='_compute_sale_order_count')
    invoice_ids = fields.One2many('account.move', 'service_order_id')
    invoice_count = fields.Integer(compute='_compute_invoice_count')
    available_fleet_vehicle_ids = fields.Many2many('fleet.vehicle', compute='_compute_available_fleet_vehicle_ids', store=False)
    fleet_vehicle_id = fields.Many2one('fleet.vehicle')
    fleet_vehicle_make = fields.Many2one('fleet.vehicle.model.brand', related='fleet_vehicle_id.model_id.brand_id')
    fleet_vehicle_model = fields.Many2one('fleet.vehicle.model', related='fleet_vehicle_id.model_id')
    fleet_vehicle_year = fields.Char(related='fleet_vehicle_id.model_year')
    fleet_vehicle_vin_sn = fields.Char(related='fleet_vehicle_id.vin_sn')
    fleet_vehicle_stock_number = fields.Char(related='fleet_vehicle_id.stock_number')
    fleet_vehicle_body_number = fields.Char(related='fleet_vehicle_id.body_number')
    fleet_vehicle_body_number = fields.Char(related='fleet_vehicle_id.body_number')
    fleet_vehicle_ymm = fields.Char(compute='_compute_fleet_vehicle_ymm')
    fleet_vehicle_warranty_line = fields.One2many('fleet.vehicle.warranty.line',related='fleet_vehicle_id.fleet_vehicle_warranty_line')
    fleet_odometer_unit = fields.Selection(related='fleet_vehicle_id.odometer_unit')
    fleet_odometer_in = fields.Integer()
    fleet_odometer_out = fields.Integer()
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
    worksheet_references = fields.Json(string="Worksheets", compute="_compute_worksheet_references")
    worksheet_references_count = fields.Integer(string="Worksheets", compute="_compute_worksheet_references")
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
    
    @api.depends('warranty_partner_id', 'service_order_lines.ttype')
    def _compute_seperate_warranty_docs(self):
        for record in self:
            is_warranty = False
            has_warranty_partner = bool(record.warranty_partner_id)
            has_warranty_line = any(x.ttype == 'Warranty' for x in record.service_order_lines)
            if has_warranty_line and has_warranty_partner:
                is_warranty = True
            record.seperate_warranty_docs = is_warranty
    
    @api.depends('sale_order_ids')
    def _compute_sale_order_count(self):
        for record in self:
            record.sale_order_count = len(record.sale_order_ids)

    @api.depends('invoice_ids')
    def _compute_sale_order_count(self):
        for record in self:
            record.invoice_count = len(record.invoice_ids)

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
            task_ids = record.service_order_lines.mapped('task_id')
            record.task_ids = task_ids
            record.task_ids_count = len(task_ids)
    
    @api.depends('service_order_lines.service_order_line_product_ids.quantity',
        'service_order_lines.service_order_line_product_ids.unit_price',
        'service_order_lines.service_order_line_service_ids.quantity',
        'service_order_lines.service_order_line_service_ids.unit_price',
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
    
    @api.depends('service_order_lines.task_id.worksheet_template_id')
    def _compute_worksheet_references(self):
        for order in self:
            worksheet_references = []
            for line in order.service_order_lines:
                if line.task_id and line.task_id.worksheet_template_id:
                    worksheet_model_name = line.task_id.worksheet_template_id.model_id.model
                    if worksheet_model_name:
                        worksheet_model = self.env[worksheet_model_name]
                        related_worksheets = worksheet_model.search([('x_project_task_id', '=', line.task_id.id)])
                        for worksheet in related_worksheets:
                            worksheet_references.append({
                                'model': worksheet_model_name, 
                                'id': worksheet.id,
                                'task_id':line.task_id.id
                            })
            order.worksheet_references = worksheet_references
            order.worksheet_references_count = len(worksheet_references)
    
    def action_open_portal(self):
        url = "https://vantage.blue-bird.com/Portal/Unit-Dashboard.aspx?search="
        if not url:
            raise UserError('Base URL is not defined in the settings')
        return {
        "type": "ir.actions.act_url",
        "url": f'{url}{self.fleet_vehicle_body_number}',
        "target": "new",  
        "url": f'{url}{self.fleet_vehicle_body_number}',
        "target": "new",  
        }
    
    def action_view_worksheets(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Worksheets'),
            'view_mode': 'tree',
            'res_model': 'service.order.worksheets',
            'context': {'service_order_ids': self.ids},
            'target': 'current',
        }
    
    def action_upsert_so(self):
        for record in self:
            for batch in record._get_so_vals():
                if batch.get('so_vals') and batch.get('existing_sale_order'):
                    batch.get('existing_sale_order').write(batch.get('so_vals'))
                elif batch.get('so_vals'):
                    record.sale_order_ids += self.env['sale.order'].create(batch.get('so_vals'))
                record.state = 'quote' if record.state == 'draft' else record.state

    def action_create_tasks(self):
        warning_service_line_names = []
        for record in self:
            for line in record.service_order_lines.filtered(lambda x: not x.task_id ):
                if not line.project_id:
                    warning_service_line_names.append(str(line.sequence))
                    continue
                line.task_id = self.env['project.task'].create(record._get_task_vals(line))
            record.state = 'confirmed'
        if warning_service_line_names:
            warning_message = 'Not all tasks were created because some service lines do not have a project defined. Line numbers to review are: '
            warning_message += "[" + ", ".join(warning_service_line_names) + "]"
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': warning_message,
                    'type': 'danger', 
                    'sticky': True, 
                }
            }

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
    
    def action_stat_button_sale_order_ids(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Orders',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'context' : {

            },
            'domain': [('id', 'in', self.sale_order_ids.ids)]
        }

    def action_stat_button_account_move_ids(self):
        action = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')
        action['domain'] = [('id', 'in', self.invoice_ids.ids)]
        ctx = {
            'default_partner_id': self.partner_id.id,
            'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
            'default_invoice_origin': self.name,
        }
        if self.shipping_partner_id:
            ctx.update({'default_partner_shipping_id': self.shipping_partner_id.id,})
        action['context']
        return action
  
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
        so_batch_vals=[]
        for sale_order_type in ['customer','warranty']:
            if sale_order_type == 'warranty' and not self.seperate_warranty_docs:
                continue
            existing_sale_order = self.sale_order_ids.filtered(lambda x: x.service_order_type == sale_order_type)
            if len(existing_sale_order) > 1:
                existing_sale_order[0]
            so_line_vals=[]
            for line in self.service_order_lines:
                if line.ttype == 'Customer' and sale_order_type == 'warranty':
                    continue
                so_line_vals.extend(self._get_so_line_section_note_details(line, order_id=existing_sale_order))
                so_line_vals.extend(self._get_so_line_details(line, order_id=existing_sale_order, ttype=sale_order_type ))
            so_vals = {}
            if so_line_vals:
                partner_id = self.partner_id
                if sale_order_type == 'warranty' and self.warranty_partner_id:
                    partner_id = self.warranty_partner_id
                so_vals = {
                    'partner_id' : partner_id.id,
                    'client_order_ref': self.ref,
                    'order_line': so_line_vals,
                    'payment_term_id': self.payment_term_id.id,
                    'user_id': self.service_writer_id.id,
                    'service_order_id': self.id,
                    'service_order_type' : sale_order_type
                }
                if self.shipping_partner_id:
                    so_vals['partner_shipping_id'] = self.shipping_partner_id.id
                so_batch_vals.append({
                    'so_vals': so_vals,
                    'existing_sale_order': existing_sale_order
                    })
        return so_batch_vals
    
    def _get_so_line_section_note_details(self, service_line, order_id=False):
        so_line_vals = []
        sol_service_details = service_line.sale_line_ids.filtered(lambda x: x.display_type_ccc and x.order_id == order_id)
        for ttype in ['section','name','cause','correction']:
            so_line_id = sol_service_details.filtered(lambda x: x.display_type_ccc == ttype)
            name=""
            sequence = service_line.sequence * 1000
            if ttype == 'section':
                name = f"{service_line.ttype} Service Issue #{service_line.sequence}"
                sequence = sequence
            elif ttype == 'name':
                name = f"Description: {service_line.name or ''}"
                sequence = sequence + 1
            elif ttype == 'cause':
                name = f"Cause: {service_line.cause or ''}",
                sequence = sequence + 2
            elif ttype == 'correction':
                name = f"Fix: {service_line.correction or ''}",
                sequence = sequence + 3
            vals = {
                'display_type' : 'line_section' if ttype == 'section' else 'line_note',
                'name': name,
                'sequence':sequence,
                'display_type_ccc': ttype,
                'service_order_line_id':service_line.id
            }
            if so_line_id:
                so_line_vals.append((1,so_line_id.id,vals))
            else:
                so_line_vals.append((0,0,vals))
        return so_line_vals

    def _get_so_line_details(self, service_line, order_id=False, ttype='customer'):
        so_line_vals = []
        line_service_ids = service_line.service_order_line_service_ids
        line_product_ids = service_line.service_order_line_product_ids
        sequence = (service_line.sequence * 1000) + 10
        for line_product in line_product_ids:
            vals = {
                'product_id': line_product.product_id.id,
                'product_uom_qty': line_product.quantity,
                'price_unit': 0 if ttype =='customer' and service_line.ttype == 'Warranty' else line_product.unit_price,
                'sequence': sequence,
                'service_order_line_id': service_line.id,
                'service_order_line_product_id': line_product.id
            }
            existing_sale_line_id = line_product.sale_line_id.filtered(lambda x: x.order_id == order_id)
            if existing_sale_line_id:
                so_line_vals.append((1, existing_sale_line_id.id, vals))
            else:
                so_line_vals.append((0, 0, vals))
            sequence += 1
        sequence = (service_line.sequence * 1000) + 500
        for line_service in line_service_ids:
            vals = {
                'product_id': line_service.product_id.id,
                'product_uom_qty': line_service.quantity,
                'price_unit': 0 if ttype =='customer' and service_line.ttype == 'Warranty' else line_service.unit_price,
                'sequence': sequence,
                'service_order_line_id': service_line.id,
                'service_order_line_service_id': line_service.id
            }
            existing_sale_line_id = line_service.sale_line_id.filtered(lambda x: x.order_id == order_id)
            if existing_sale_line_id:
                so_line_vals.append((1, existing_sale_line_id.id, vals))
            else:
                so_line_vals.append((0, 0, vals))
            sequence += 1
        return so_line_vals


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
