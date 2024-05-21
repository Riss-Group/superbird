from odoo import models, fields, api
from odoo.exceptions import UserError


class ServiceLineViewProduct(models.Model):
    _name = 'service.line.view.product'
    _description = 'Service Line View Product'

    service_order_line_id = fields.Many2one('service.order.line')
    service_order_id = fields.Many2one('service.order', related='service_order_line_id.service_order_id')
    service_order_line_product_ids = fields.One2many('service.order.line.product',
                                                     related='service_order_line_id.service_order_line_product_ids',
                                                     readonly=False)
    service_order_line_item_ids = fields.One2many('service.order.line.product',
                                                     related='service_order_line_id.service_order_line_item_ids',
                                                     readonly=False)
    service_order_line_labor_ids = fields.One2many('service.order.line.product',
                                                     related='service_order_line_id.service_order_line_labor_ids',
                                                     readonly=False)

    @api.model
    def default_get(self, fields_list):
        '''
            Base Override
            Sets the initial default for service_order_line_id from context

            Returns:
                defaults dict
        '''
        res = super().default_get(fields_list)
        res['service_order_line_id'] = int(self.env.context.get('service_order_line_id', 0))
        return res

    def action_save(self):
        return True
