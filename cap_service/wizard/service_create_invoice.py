from odoo import  models, fields, api, _
from odoo.exceptions import UserError
from markupsafe import Markup


class ServiceCreateInvoice(models.TransientModel):
    _name = 'service.create.invoice'
    _description = 'Service Create Invoice'


    service_order_id = fields.Many2one('service.order')
    available_service_line_ids = fields.Many2many('service.order.line', compute='_compute_available_service_line_ids')
    selected_service_line_ids = fields.Many2many('service.order.line')

    @api.depends('service_order_id')
    def _compute_available_service_line_ids(self):
        for record in self:
            record.available_service_line_ids = self.env['service.order.line'].search([
                ('service_order_id','=',record.service_order_id.id),
                ('task_state','=','done'),
                ('should_invoice','=',True)
        ])

    def button_save(self):
        self.ensure_one()
        if not self.selected_service_line_ids:
            return True
        service_order = self.service_order_id
        invoice_vals_list = service_order._get_invoice_vals(self.selected_service_line_ids)
        created_invoices = self.env['account.move']
        for invoice_val in invoice_vals_list:
            created_invoices += self.env['account.move'].create(invoice_val)
        message_list = [
            f"<li>Line [{line.sequence}-{line.ttype}]: Description - {line.name or 'No description'}</li>"
            for line in self.selected_service_line_ids
        ]
        message_body = f"<b>Invoices created for service lines:</b><br><ul>{''.join(message_list)}</ul>"
        service_order.message_post(body=Markup("%s" % (_(message_body))), subtype_xmlid="mail.mt_note")
        if all(service_order.service_order_lines.mapped('fully_invoiced')):
            service_order.state = 'done'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', created_invoices.ids)],
            'target': 'current',
        }
