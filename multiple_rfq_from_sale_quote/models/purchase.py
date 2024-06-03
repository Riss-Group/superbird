# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    custom_sale_order_id = fields.Many2one(
        'sale.order',
        string='Sales Order'
    )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: