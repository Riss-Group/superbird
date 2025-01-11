# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    shipping_rates_all_ids = fields.One2many('shipping.rates.all', 'choose_delivery_carrier_id')
    carrier_id = fields.Many2one(
        'delivery.carrier',
        string="Shipping Method",
        required=False,
    )
    def get_all_rates(self):
        carriers_ids = self.env['delivery.carrier'].search(
            ['|', ('company_id', '=', False), ('company_id', '=', self.order_id.company_id.id)])
        lst_carrier = []
        for carrier in carriers_ids:
            vals = carrier.rate_shipment(self.order_id)
            vals_dict = {
                'order_id': self.order_id.id,
                'carrier_id': carrier.id,
                'choose_delivery_carrier_id': self.id
            }
            if vals.get('success'):
                vals_dict['msg'] = vals.get('warning_message', False)
                vals_dict['delivery_price'] = vals['price']
                vals_dict['display_price'] = vals['carrier_price']
                vals_dict['success'] = True
            else:
                vals_dict['msg'] = vals['error_message']
            lst_carrier.append((0,0, vals_dict))
        if lst_carrier:
            self.shipping_rates_all_ids = False
            self.shipping_rates_all_ids = lst_carrier
        return {
            'name': _('Add a shipping method'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.delivery.carrier',
            'res_id': self.id,
            'target': 'new',
        }

    def button_confirm(self):
        selected_carrier_line_id = self.shipping_rates_all_ids.filtered(lambda l:l.select)
        if not selected_carrier_line_id:
            raise UserError(_('Please select at least one shipping method.'))
        if len(selected_carrier_line_id) > 1:
            raise UserError(_('You can select only one shipping method.'))
        self.carrier_id = selected_carrier_line_id.carrier_id.id
        self._onchange_carrier_id()
        vals = self.carrier_id.rate_shipment(self.order_id)
        if vals.get('success'):
            self.delivery_message = vals.get('warning_message', False)
            self.delivery_price = vals['price']
            self.display_price = vals['carrier_price']
        self.order_id.set_delivery_line(self.carrier_id, self.delivery_price)
        self.order_id.write({
            'recompute_delivery_price': False,
            'delivery_message': self.delivery_message,
        })


class ShippingRatesAll(models.TransientModel):
    _name = 'shipping.rates.all'
    _description = "Shipping Rates All Wizard"

    order_id = fields.Many2one('sale.order', required=True, ondelete="cascade")
    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', required=True)
    carrier_id = fields.Many2one(
        'delivery.carrier',
        string="Shipping Method",
        required=True,
    )
    delivery_type = fields.Selection(related='carrier_id.delivery_type')
    carrier_id = fields.Many2one(
        'delivery.carrier',
        string="Shipping Method",
        required=True,
    )
    delivery_price = fields.Float()
    display_price = fields.Float(string='Cost', readonly=True)
    currency_id = fields.Many2one('res.currency', related='order_id.currency_id')
    company_id = fields.Many2one('res.company', related='order_id.company_id')
    order_id = fields.Many2one('sale.order', required=True, ondelete="cascade")
    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', required=True)
    choose_delivery_carrier_id = fields.Many2one('choose.delivery.carrier', string="Choose Carrier")
    select = fields.Boolean(string="Select")
    msg = fields.Text(string="Warnings/Errors")
    success = fields.Boolean(string="Success")