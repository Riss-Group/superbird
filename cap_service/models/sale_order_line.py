from odoo import fields, models, api


class SalesOrderLine(models.Model):
    _inherit = 'sale.order.line'

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