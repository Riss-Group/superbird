from odoo import  models, fields, api, _, Command
from odoo.exceptions import UserError, ValidationError
from markupsafe import Markup
import logging
logger = logging.getLogger(__name__)


class ServiceOrder(models.Model):
    _name = 'service.order' 
    _description = "Service Order"  
    _order = 'priority desc, name desc, end_date desc , id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    

    name = fields.Char(default=lambda self: '', copy=False)
    partner_id = fields.Many2one('res.partner', tracking=True)
    warranty_partner_id = fields.Many2one('res.partner', tracking=True) #How do I remove this deprecated field without an error
    service_order_lines = fields.One2many('service.order.line', 'service_order_id', )
    sale_order_ids = fields.Many2many('sale.order', compute='_compute_sale_orders', store=True, readonly=False, copy=False)
    sale_order_count = fields.Integer(compute='_compute_sale_orders',store=True)
    picking_ids = fields.Many2many('stock.picking', compute="_compute_picking_ids")
    rental_order_ids = fields.One2many('sale.order', 'service_order_rental_id')
    rental_order_count = fields.Integer(compute='_compute_rental_order_count')
    invoice_ids = fields.One2many('account.move', 'service_order_id')
    invoice_count = fields.Integer(compute='_compute_invoice_count')
    show_invoice_button = fields.Boolean(compute='_compute_show_invoice_button')
    available_fleet_vehicle_ids = fields.Many2many('fleet.vehicle', compute='_compute_available_fleet_vehicle_ids', store=False)
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', tracking=True)
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
    internal_memo = fields.Text()
    printed_memo = fields.Text()
    ref = fields.Char()
    currency_id = fields.Many2one('res.currency', compute='_compute_currency_id', store=True, readonly=False)
    total = fields.Monetary(compute="_compute_totals")
    customer_total = fields.Monetary(compute="_compute_totals")
    customer_parts_total = fields.Monetary(compute="_compute_totals")
    customer_service_total = fields.Monetary(compute="_compute_totals")
    warranty_total = fields.Monetary(compute="_compute_totals")
    warranty_parts_total = fields.Monetary(compute="_compute_totals")
    warranty_service_total = fields.Monetary(compute="_compute_totals")
    internal_total = fields.Monetary(compute='_compute_totals')
    internal_parts_total = fields.Monetary(compute='_compute_totals')
    internal_service_total = fields.Monetary(compute='_compute_totals')
    service_writer_id = fields.Many2one('res.users', default=lambda self: self.env.user if self.env.context.get('is_repair_order') else False, tracking=True)
    payment_term_id = fields.Many2one('account.payment.term', compute='_compute_payment_term_id', store=True, readonly=False)
    start_date = fields.Datetime(default=fields.Datetime.now(), tracking=True)
    end_date = fields.Datetime(tracking=True)
    task_ids = fields.Many2many('project.task', compute='_compute_task_ids')
    task_ids_count = fields.Integer(compute='_compute_task_ids')
    show_task_button = fields.Boolean(compute='_compute_show_task_button')
    worksheet_references = fields.Json(string="Worksheets", compute="_compute_worksheet_references")
    worksheet_references_count = fields.Integer(string="Worksheets", compute="_compute_worksheet_references")
    state = fields.Selection([
        ('draft','Draft'),
        ('quote','Quote'),
        ('confirmed','In Repair'),
        ('done','Done'),
        ],default='draft', tracking=True)
    priority = fields.Selection(selection=[
        ('0','Low'),
        ('1','low'),
        ('2','med-low'),
        ('3','med'),
        ('4','med-high'),
        ('5','high'),
    ],default='1')
    company_id = fields.Many2one(comodel_name='res.company', required=True, index=True, default=lambda self: self.env.company)
    branch_company_ids = fields.Many2many('res.company', compute="_compute_branch_company_ids", store=True, readonly=False)

    @api.constrains('state','fleet_vehicle_id','start_date')
    def _check_state_fleet_date(self):
        for record in self:
            if record.state != 'draft' and (not record.fleet_vehicle_id or not record.start_date):
                raise ValidationError(_("The vehicle and start date must be set before changing the state to anything other than 'Draft'."))
    
    @api.constrains('start_date', 'end_date')
    def _check_start_end_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date > record.end_date:
                    raise ValidationError(
                        _("The start date must be earlier than the end date:\n\nRecord id/name: %(id)s, %(name)s\nStart Date: %(start_date)s\nEnd Date: %(end_date)s.") % {
                            'name': record.display_name,
                            'id': record.id,
                            'start_date': record.start_date,
                            'end_date': record.end_date,
                        }
                    )

    @api.onchange('fleet_vehicle_id')
    def _onchange_fleet_vehicle_id(self):
        for record in self:
            record.fleet_odometer_in = record.fleet_vehicle_id.odometer
            record.fleet_odometer_unit = record.fleet_vehicle_id.odometer_unit
            record.partner_id = record.fleet_vehicle_id.customer_id
            
    @api.depends('fleet_vehicle_id')
    def _compute_fleet_vehicle_ymm(self):
        for record in self:
            record.fleet_vehicle_ymm = f"{record.fleet_vehicle_id.model_year or 'NA'}/{record.fleet_vehicle_make.name or 'NA'}/{record.fleet_vehicle_id.model_id.name or 'NA'}"
    
    @api.depends('partner_id')
    def _compute_payment_term_id(self):
        for order in self:
            order.payment_term_id = order.partner_id.property_payment_term_id            
    
    @api.depends('partner_id')
    def _compute_available_fleet_vehicle_ids(self):
        for record in self:
            if record.partner_id:
                partner_domain = ['|', ('customer_id','=',record.partner_id.id), ('customer_id', 'child_of', [record.partner_id.id])]
                record.available_fleet_vehicle_ids = self.env['fleet.vehicle'].search(partner_domain)
            else:
                record.available_fleet_vehicle_ids = self.env['fleet.vehicle'].search([])
      
    @api.depends('service_order_lines.sale_line_ids', 'service_order_lines')
    def _compute_sale_orders(self):
        for record in self:
            sale_order_ids = record.service_order_lines.sale_line_ids.mapped('order_id')
            record.sale_order_ids = sale_order_ids.ids
            record.sale_order_count = len(sale_order_ids)
    
    @api.depends('sale_order_ids')
    def _compute_picking_ids(self):
        for record in self:
            record.picking_ids = record.sale_order_ids.picking_ids
    
    @api.depends('rental_order_ids')
    def _compute_rental_order_count(self):
        for record in self:
            record.rental_order_count = len(record.rental_order_ids)

    @api.depends('service_order_lines.task_id', 'service_order_lines')
    def _compute_show_task_button(self):
        for record in self:
            record.show_task_button = any(record.service_order_lines.filtered(lambda x: not x.task_id))

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = len(record.invoice_ids)
    
    @api.depends('service_order_lines.should_invoice', 'service_order_lines')
    def _compute_show_invoice_button(self):
        for record in self:
            record.show_invoice_button = any(record.service_order_lines.filtered(lambda x: x.should_invoice))

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
    
    @api.depends('company_id')
    def _compute_currency_id(self):
        for record in self:
            record.currency_id = record.company_id.currency_id
    
    @api.depends('company_id')
    def _compute_branch_company_ids(self):
        for record in self:
            if record.company_id:
                company_id = record.company_id.parent_id if record.company_id.parent_id else record.company_id
                linked_companies = [
                    company_id.service_branch_id,
                    company_id.parts_branch_id,
                    company_id.sales_branch_id,
                    company_id
                ]
                record.branch_company_ids = [(6, 0, {c.id for c in linked_companies if c})]
            else:
                record.branch_company_ids = [(5,)] 
    
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
                    record.message_post(
                        body=Markup("<b>%s</b> %s") % (_("Sale Order Updated:"), batch.get('existing_sale_order').name),
                        subtype_xmlid="mail.mt_note"
                    )
                elif batch.get('so_vals'):
                    sale_order_id = self.env['sale.order'].create(batch.get('so_vals'))
                    record.message_post(
                        body=Markup("<b>%s</b> %s") % (_("Sale Order Created:"), sale_order_id.name),
                        subtype_xmlid="mail.mt_note"
                    )
                record.state = 'quote' if record.state == 'draft' else record.state

    def action_create_tasks(self):
        warning_service_line_names = []
        for record in self:
            for line in record.service_order_lines.filtered(lambda x: not x.task_id ):
                if not line.project_id:
                    warning_service_line_names.append(str(line.sequence))
                    continue
                line.task_id = self.env['project.task'].create(record._get_task_vals(line))
                record.message_post(
                    body=Markup("<b>%s</b> %s") % (_("Task Created:"), line.task_id.name),
                    subtype_xmlid="mail.mt_note"
                )
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

    def button_create_rental_order(self):
        return {
            'name': 'Create Rental Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'service.rental.order',
            'context': {
                'default_service_order_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_start_date': self.start_date,
                'default_end_date': self.end_date,
                'default_company_id':self.company_id.id
            },
            'target': 'new',
        }

    def button_create_invoices(self):
        return {
            'name': 'Create Invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'service.create.invoice',
            'context': {
                'default_service_order_id': self.id,
            },
            'target': 'new',
        }

    def button_create_backorder(self):
        return {
            'name': 'Create Backourder',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'service.create.backorder',
            'context': {
                'default_service_order_id': self.id,
            },
            'target': 'new',
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
    
    def action_stat_button_rental_order_ids(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("sale_renting.rental_order_action")
        action['domain'] = [('id', 'in', self.rental_order_ids.ids)]
        return action

    def action_stat_button_account_move_ids(self):
        action = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')
        action['domain'] = [('id', 'in', self.invoice_ids.ids)]
        ctx = {
            'default_partner_id': self.partner_id.id,
            'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
            'default_invoice_origin': self.name,
        }
        action['context']
        return action
  
    def action_view_delivery(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        pickings = self.sale_order_ids.picking_ids
        action['domain'] = [('id', 'in', pickings.ids)]
        #Dont allow create since context will be dirty since there are multiple SOs Involved
        action['context'] = {'create': 0}
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
    
    def _display_line_missing_product_id_error(self, service_order_line=False):
        if not service_order_line:
            return False
        product_lines = service_order_line.service_order_line_product_ids.filtered(lambda x: not x.product_id)
        service_lines = service_order_line.service_order_line_service_ids.filtered(lambda x: not x.product_id)
        if product_lines or service_lines:
            message = f"Service Order Line {service_order_line.sequence} is missing a product id on one of the product/service lines."
            raise UserError(message)
    
    def _get_task_vals(self, line):
        self.ensure_one()
        self._display_line_missing_product_id_error(line)
        task_vals = {
            'name': f"{self.name} - Line: {line.sequence}",
            'description': line.name,
            'project_id': line.project_id.id,
            'planned_date_begin': self.start_date,
            'date_deadline': self.end_date,
            'fleet_vehicle_id': self.fleet_vehicle_id.id,
            'user_ids': False,
            'allocated_hours': line.hours,
            'partner_id': self.partner_id.id,
            'worksheet_template_id': line.service_template_id.worksheet_template_id.id,
            'service_order_id': line.service_order_id.id,
            'service_order_line_id': line.id
        }
        return task_vals

    def _get_so_vals(self):
        self.ensure_one()
        so_batch_vals = []
        grouped_lines = {}
        for line in self.service_order_lines:
            self._display_line_missing_product_id_error(line)
            key = (line.bill_to_partner_id, line.ttype)
            if key not in grouped_lines:
                grouped_lines[key] = self.env['service.order.line']
            grouped_lines[key] |= line
        for (bill_to_partner, ttype), lines in grouped_lines.items():
            existing_sale_order = self.sale_order_ids.filtered(lambda so: so.partner_id == bill_to_partner and so.service_order_type == ttype)
            so_line_vals = []
            for line in lines:
                so_line_vals.extend(self._get_so_line_section_note_details(line, order_id=existing_sale_order))
                so_line_vals.extend(self._get_so_line_details(line, order_id=existing_sale_order))
            if so_line_vals:
                so_vals = {
                    'partner_id': bill_to_partner.id,
                    'client_order_ref': self.ref,
                    'order_line': so_line_vals,
                    'payment_term_id': self.payment_term_id.id,
                    'user_id': self.service_writer_id.id,
                    'service_order_id': self.id,
                    'service_order_type': ttype, 
                    'company_id': self.company_id.id,
                }
                so_batch_vals.append({
                    'so_vals': so_vals,
                    'existing_sale_order': existing_sale_order,
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

    def _get_so_line_details(self, service_line, order_id=False):
        so_line_vals = []
        line_service_ids = service_line.service_order_line_service_ids
        line_product_ids = service_line.service_order_line_product_ids
        sequence = (service_line.sequence * 1000) + 10
        for line_product in line_product_ids:
            vals = {
                'product_id': line_product.product_id.id,
                'product_uom_qty': line_product.quantity,
                'price_unit': line_product.unit_price,
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
            product_uom_qty = line_service.quantity
            if service_line.bill_type == 'actual':
                product_uom_qty = line_service.quantity_consumed
            vals = {
                'product_id': line_service.product_id.id,
                'product_uom_qty': product_uom_qty,
                'price_unit': line_service.unit_price,
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
    
    def _get_invoice_vals(self, service_lines):
        self.ensure_one()
        invoice_batches = []
        grouped_lines = {}
        for line in service_lines:
            key = (line.bill_to_partner_id, line.ttype)
            if key not in grouped_lines:
                grouped_lines[key] = self.env['service.order.line']
            grouped_lines[key] |= line
        for (partner, ttype), lines in grouped_lines.items():
            invoice_line_vals = []
            for line in lines:
                section_note_details = self._get_invoice_line_section_note_details(line)
                for section_note in section_note_details:
                    invoice_line_vals.append((0, 0, section_note))
                product_service_details = self._get_invoice_line_details(line)
                for product_service in product_service_details:
                    invoice_line_vals.append((0, 0, product_service))
            if invoice_line_vals:
                invoice_vals = {
                    'partner_id': partner.id,
                    'move_type': 'out_invoice',
                    'service_order_type' : ttype,
                    'ref': self.ref,
                    'invoice_date': fields.Date.context_today(self),
                    'invoice_origin': self.name,
                    'invoice_line_ids': invoice_line_vals,
                    'company_id': self.company_id.id,
                }
                invoice_batches.append(invoice_vals)
        return invoice_batches

    def _get_invoice_line_section_note_details(self, service_line):
        invoice_line_vals = []
        sequence = service_line.sequence * 1000
        invoice_line_vals.append({
            'display_type': 'line_section',
            'name': f"{service_line.ttype} Service Issue #{service_line.sequence}",
            'sequence': sequence,
        })
        sequence += 1
        if service_line.name:
            invoice_line_vals.append({
                'display_type': 'line_note',
                'name': f"Description: {service_line.name}",
                'sequence': sequence,
            })
            sequence += 1
        if service_line.cause:
            invoice_line_vals.append({
                'display_type': 'line_note',
                'name': f"Cause: {service_line.cause}",
                'sequence': sequence,
            })
            sequence += 1
        if service_line.correction:
            invoice_line_vals.append({
                'display_type': 'line_note',
                'name': f"Fix: {service_line.correction}",
                'sequence': sequence,
            })
        return invoice_line_vals

    def _get_invoice_line_details(self, service_line):
        invoice_line_vals = []
        product_sequence = (service_line.sequence * 1000) + 10
        service_sequence = (service_line.sequence * 1000) + 500
        for line_product in service_line.service_order_line_product_ids:
            sale_line_ids = line_product.sale_line_id.ids if line_product.sale_line_id else []
            invoice_line_vals.append({
                'product_id': line_product.product_id.id,
                'quantity': line_product.qty_to_invoice,
                'price_unit': line_product.unit_price,
                'name': line_product.product_id.display_name or 'NA',
                'sequence': product_sequence,
                'service_order_line_id': service_line.id,
                'service_order_line_product_id': line_product.id,
                'sale_line_ids': [(6, 0, sale_line_ids)] if sale_line_ids else [],
            })
            product_sequence += 1
        for line_service in service_line.service_order_line_service_ids:
            sale_line_ids = line_service.sale_line_id.ids if line_service.sale_line_id else []
            invoice_line_vals.append({
                'product_id': line_service.product_id.id,
                'quantity': line_service.qty_to_invoice,
                'price_unit': line_service.unit_price,
                'name': line_service.product_id.display_name or 'NA',
                'sequence': service_sequence,
                'service_order_line_id': service_line.id,
                'service_order_line_service_id': line_service.id,
                'sale_line_ids': [(6, 0, sale_line_ids)] if sale_line_ids else [],
            })
            service_sequence += 1
        return invoice_line_vals

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
            task_vals = {}
            if vals.get('start_date') or vals.get('end_date'):
                task_ids = rec.service_order_lines.task_id.filtered(lambda x: not x.stage_id.is_done_stage and not x.stage_id.is_wip_stage)
                if task_ids:
                    task_vals.update({
                        'planned_date_begin': rec.start_date,
                        'date_deadline': rec.end_date,
                    })
            if vals.get('priority'):
                task_ids = rec.service_order_lines.task_id.filtered(lambda x: not x.stage_id.is_done_stage and not x.stage_id.is_wip_stage)
                if task_ids:
                    task_vals.update({
                        'priority': rec.priority,
                    })
            if task_vals:
                task_ids.write(task_vals)
        return result
