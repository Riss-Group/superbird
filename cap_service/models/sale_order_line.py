from odoo import fields, models, api


class SalesOrderLine(models.Model):
    _inherit = 'sale.order.line'

    service_order_line_id = fields.Many2one('service.order.line')
    ttype = fields.Char(compute='_compute_service_line_info', store=True)
    item_type = fields.Selection(related='product_id.detailed_type')
    display_type_ccc = fields.Selection([
        ('name', 'Complaint'),
        ('cause', 'Cause'),
        ('correction', 'Fix')
    ])
    
    @api.depends('service_order_line_id.ttype', 'service_order_line_id.name', 'service_order_line_id.cause', 'service_order_line_id.correction')
    def _compute_service_line_info(self):
        for record in self:
            record.ttype = record.service_order_line_id.ttype
            if record.display_type == 'line_note' and record.display_type_ccc:
                ccc_label = self.get_selection_label('sale.order.line', 'display_type_ccc', record.display_type_ccc)
                record.name = f"{ccc_label}: {record.service_order_line_id[record.display_type_ccc] or ''}"
    
    def get_selection_label(self, object, field_name, field_value):
        '''
            This method allows us to get the label value for the selection field
        '''
        if field_value:
            return (dict(self.env[object].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])
        else:
            return False

    service_order_line_product_id = fields.Many2one('service.order.line.product')