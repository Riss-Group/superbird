# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    custom_vendor_ids = fields.Many2many(
        'res.partner',
        string="Vendors",
        compute="_compute_vendor",
        store=True,
        readonly=False,
    )
    is_rfq_create = fields.Boolean(
        related='order_id.is_rfq_create',
        string="Create RFQ?",
    )

    @api.depends('product_id')
    def _compute_vendor(self):
        for rec in self:
            rec.custom_vendor_ids = rec.product_id.seller_ids.filtered(
                lambda x: x.company_id.id == rec.company_id.id or not x.company_id).mapped('partner_id')

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    is_rfq_create = fields.Boolean(
        string="Create RFQ?",
        default = True
    )

    def probc_get_purchase_order(self):
        # for rec in self:
        #     purchase_orders = self.env['purchase.order'].search([('custom_sale_order_id', '=', rec.id)])
        #     action = self.env.ref('purchase.purchase_form_action')
        #     result = action.sudo().read()[0]
        #     result.update({'domain': [('custom_sale_order_id', '=', rec.id)]})
        # return result
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_form_action')
        action['domain'] = [('custom_sale_order_id','=', self.id)]
        return action

    def create_rfq_from_sales(self):
        for rec in self:
            purchase_order_obj = self.env['purchase.order']
            po_line_obj = self.env['purchase.order.line']
            vendor_dict = {}
            order_ids = []
            for line in rec.order_line:
                if line.custom_vendor_ids:
                    for vendor in line.custom_vendor_ids:
                        if vendor.id in vendor_dict:
                            po = vendor_dict.get(vendor.id)
                            #Create a 'purchase line'.
                            order_line_vals = rec._probc_prepare_purchase_order_line(po, line)
                            purchase_order_line = po_line_obj.create(order_line_vals)
                        else:
                            list_vals = rec._probc_prepare_purchase_order(rec, vendor)
                            po = purchase_order_obj.create(list_vals)
                            order_ids.append(po.id)
                            message = _("This Purchase has been created from the Sales Order: <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a>") % (rec.id, rec.name)
                            po.message_post(body=message)
                            vendor_dict.update({vendor.id: po})

                            #Create a 'purchase line'.
                            order_line_vals = rec._probc_prepare_purchase_order_line(po, line)
                            purchase_order_line = po_line_obj.create(order_line_vals)

            res = self.env.ref('purchase.purchase_form_action')
            res = res.sudo().read()[0]
            res['domain'] = str([('id','in',order_ids)])
            return res

    def _probc_prepare_purchase_order(self, sale_orders, partner):
        sale_order_id = sale_orders 
        purchase_order_obj = self.env['purchase.order']
        # fpos = self.env['account.fiscal.position'].with_context(\
        #         company_id=sale_order_id.company_id.id).get_fiscal_position(partner.id)
        vals = {
            'partner_id': partner.id,
            'picking_type_id': self._get_picking_type(sale_order_id.company_id),
            'company_id': sale_order_id.company_id.id,
            'currency_id': partner.property_purchase_currency_id.id \
                            or self.env.user.company_id.currency_id.id,
            'origin': sale_order_id.name,
            'payment_term_id': partner.property_supplier_payment_term_id.id,
            'date_order': sale_order_id.date_order,
            # 'fiscal_position_id': fpos,
            'custom_sale_order_id':sale_order_id.id
        }
        new_line = purchase_order_obj.with_context(lang=sale_order_id.partner_id.lang).new(vals)
        new_line.onchange_partner_id()
        new_line._compute_tax_id()
        new_line.onchange_partner_id_warning()
        list_vals = purchase_order_obj._convert_to_write({
            name: new_line[name] for name in new_line._cache
        })
        return list_vals

    def _probc_prepare_purchase_order_line(self, po, line):
        po_line_obj = self.env['purchase.order.line']
        taxes = line.product_id.supplier_taxes_id
        fpos = po.fiscal_position_id
        taxes_id = fpos.map_tax(taxes) if fpos else taxes
        if taxes_id:
            taxes_id = taxes_id.filtered(lambda x: x.company_id.id == line.company_id.id)
        date_planned = datetime.today()
        seller = line.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=line.product_uom_qty,
            date=po.date_order,
            uom_id=line.product_id.uom_po_id)
        order_line_vals = {
            'partner_id': po.partner_id.id,
            'product_qty': line.product_uom_qty,
            'product_id': line.product_id.id,
            'product_uom': line.product_id.uom_po_id.id,
            'price_unit': seller.price or 0.0,
            'date_planned': date_planned,
            'taxes_id': [(6, 0, taxes_id.ids)],
            'order_id': po.id,
        }
        new_purchase_line = po_line_obj.new(order_line_vals)
        new_purchase_line.onchange_product_id()
        new_purchase_line.onchange_product_id_warning()
        # new_purchase_line._onchange_quantity()

        purchase_line = po_line_obj._convert_to_write({
            name: new_purchase_line[name] for name in new_purchase_line._cache
        })
        purchase_line.update({
            'product_qty' : line.product_uom_qty,
            'name': line.name
        })
        return purchase_line

    @api.model
    def _get_picking_type(self, company_id=lambda self: self.env.user.company_id):
        type_obj = self.env['stock.picking.type']
        types = type_obj.search([('code', '=', 'incoming'),
                                ('warehouse_id.company_id', '=', company_id.id),])
        return types[0].id if types else False

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self:
            related_rfq = self.env['purchase.order'].search([('custom_sale_order_id', '=', rec.id)])
            for po in related_rfq:
                todos = {
                    'res_id': po.id,
                    'res_model_id': self.env['ir.model'].search([('model', '=', 'purchase.order')]).id,
                    'user_id': po.user_id.id,
                    'summary': 'Sale Order Confirmed',
                    'note': 'Related Sale Order: %s has been confirmed' % (rec.name),
                    'activity_type_id': 4,
                    'date_deadline': datetime.today(),
                    }
                self.env['mail.activity'].create(todos)
        return res
        
