from odoo import  models, fields, api
from odoo.exceptions import UserError


class ServiceTemplateSelect(models.TransientModel):
    _name = 'service.template.select'
    _description = 'Service Template Select'


    service_order_id = fields.Many2one('service.order')
    service_template = fields.Many2many('service.template')


    def button_save(self):
        for record in self.service_template:
            service_order_product_vals = [ 
                (0,0,{
                    'product_id':x.product_id.id,
                    'quantity':x.quantity,
                    'unit_price':x.product_id.list_price
                }) 
                for x in record.service_template_parts]               
            service_order_service_vals = [
                (0,0,{
                    'product_id':x.product_id.id,
                    'quantity':x.quantity,
                    'unit_price':x.product_id.list_price
                }) 
                for x in record.service_template_service]     
            service_order_line_vals = {
                'service_order_id': self.service_order_id.id,
                'op_code_id': record.id,
                'ttype': record.tttype,
                'project_id' : record.project_id.id,
                'name': record.complaint,
                'cause': record.cause,
                'correction': record.correction,
                'service_order_line_product_ids' : service_order_product_vals,
                'service_order_line_service_ids' : service_order_service_vals,
            }
            self.env['service.order.line'].create(service_order_line_vals)
        self.service_order_id.update_child_sequence()
        return True
