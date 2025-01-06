from odoo import  models, fields, api, _
from odoo.exceptions import UserError
from markupsafe import Markup


class ServiceCreateBackorder(models.TransientModel):
    _name = 'service.create.backorder'
    _description = 'Service Create Backorder'


    service_order_id = fields.Many2one('service.order')
    available_service_line_ids = fields.Many2many('service.order.line', compute='_compute_available_service_line_ids')
    selected_service_line_ids = fields.Many2many('service.order.line')

    @api.depends('service_order_id')
    def _compute_available_service_line_ids(self):
        for record in self:
            record.available_service_line_ids = self.env['service.order.line'].search([
                ('service_order_id','=',record.service_order_id.id),
                ('task_state','!=','done'),
                ('fully_invoiced','=',False)
        ])

    def button_save(self):
        self.ensure_one()
        if not self.selected_service_line_ids:
            return True
        new_service_order_id = self.service_order_id.copy()
        message_list = []
        for line in self.selected_service_line_ids:
            line.service_order_id = new_service_order_id   
            message_list.append(f"<li>Line [{line.sequence}-{line.ttype}]: Description - {line.name or 'No description'}</li>")
        message_body = f"<b>Backorder [{new_service_order_id.name}] created for service lines:</b><br><ul>{''.join(message_list)}</ul>"
        self.service_order_id.message_post(body=Markup("%s" % (_(message_body))), subtype_xmlid="mail.mt_note")
        new_message_body = f"Backorder of {self.service_order_id.name}"
        new_service_order_id.message_post(body=Markup("%s" % (_(new_message_body))), subtype_xmlid="mail.mt_note")
        for line in new_service_order_id.service_order_lines:
            line.task_id.write({
                'name': f"{new_service_order_id.name} - Line: {line.sequence}",
                'service_order_id': new_service_order_id.id,
            })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service Order',
            'view_mode': 'form',
            'res_model': 'service.order',
            'res_id': new_service_order_id.id,
            'target': 'current',
        }
