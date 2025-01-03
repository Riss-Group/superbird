from odoo import fields, models, api


class SalesOrderLine(models.Model):
    _inherit = 'sale.order.line'

    
    procurement_group_id = fields.Many2one('procurement.group', string='Procurement Group', copy=False,)
    fleet_vehicle_rental_id = fields.Many2one('fleet.vehicle', string='Fleet Vehicle')
    create_fleet_vehicle = fields.Boolean(related='product_template_id.create_fleet_vehicle')
    service_order_line_id = fields.Many2one('service.order.line')
    service_order_line_product_id = fields.Many2one('service.order.line.product', )
    service_order_line_service_id = fields.Many2one('service.order.line.service', )
    ttype = fields.Char(compute='_compute_service_line_info', store=True)
    item_type = fields.Selection(related='product_id.detailed_type')
    display_type_ccc = fields.Selection([
        ('name', 'Complaint'),
        ('cause', 'Cause'),
        ('correction', 'Fix'),
        ('section','Section')
    ])
    
    @api.depends('service_order_line_id.ttype', 'service_order_line_id.name', 'service_order_line_id.cause', 'service_order_line_id.correction')
    def _compute_service_line_info(self):
        for record in self:
            record.ttype = record.service_order_line_id.ttype
            if record.display_type == 'line_note' and record.display_type_ccc:
                ccc_label = self.get_selection_label('sale.order.line', 'display_type_ccc', record.display_type_ccc)
                record.name = f"{ccc_label}: {record.service_order_line_id[record.display_type_ccc] or ''}"

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res["service_order_line_id"] = self.service_order_line_id.id
        res["service_order_line_product_id"] = self.service_order_line_product_id.id
        res["service_order_line_service_id"] = self.service_order_line_service_id.id
        res["display_type_ccc"] = self.display_type_ccc
        return res
    
    def _get_procurement_group(self):
        procurement_group =  super()._get_procurement_group()
        if self.service_order_line_id:
            if not self.procurement_group_id:
                existing_group =  self.env['procurement.group'].search([
                    ('service_line_id', '=', self.service_order_line_id.id),
                    ('sale_id', '=', self.order_id.id)
                ], limit=1)
                if existing_group:
                    self.procurement_group_id = existing_group
                else:
                    self.procurement_group_id = self.env['procurement.group'].create({
                        'name': f"{self.order_id.name} [{self.service_order_line_id.service_order_id.name}-{self.service_order_line_id.sequence}]",
                        'move_type': self.order_id.picking_policy,
                        'sale_id': self.order_id.id,
                        'partner_id': self.order_id.partner_shipping_id.id,
                        'service_line_id': self.service_order_line_id.id
                    })
            procurement_group = self.procurement_group_id
        return procurement_group
    
    def _prepare_procurement_values(self, group_id=False):
        values = super()._prepare_procurement_values(group_id=group_id)
        if self.procurement_group_id:
            values['group_id'] = self.procurement_group_id
        return values
    
    def _prepare_procurement_group_vals(self):
        vals = super()._prepare_procurement_group_vals()
        if self.service_order_line_id:
            vals['name'] = f"{vals['name']} [{self.service_order_line_id.service_order_id.name}-{self.service_order_line_id.sequence}]"
        return vals