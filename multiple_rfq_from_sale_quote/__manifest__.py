# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Multiple Vendors RFQ from Sales Order',
    'version' : '6.1.3',
    'price' : 39.0,
    'currency': 'EUR',
    'category': 'Inventory/Purchase',
    'license': 'Other proprietary',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/multiple_rfq_from_sale_quote/202',#'https://youtu.be/jon5OQljmXE',
    'images': [
        'static/description/img.jpg',
    ],
    'summary' : 'This app allows your sales team to create multiple RFQ for selected multiple vendors.',
    'description': """
This app allows your sales team to create multiple RFQ for selected multiple vendors.
    Allow you to set multiple vendors on the sales order line.
    Based on selected vendors on the sales order line system will generate multiple RFQ per vendor.

    For more details please check below screenshots and watch the video.
    """,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'wwww.probuse.com',
    'depends' : [
        'sale_management',
        'purchase',
        'stock'
    ],
    'support': 'contact@probuse.com',
    'data' : [
       'views/sale_order_view.xml',
       'views/purchase_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
