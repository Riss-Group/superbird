# -*- coding: utf-8 -*-
{
    'name': "cap stock barcode",
    'license': 'OPL-1',

    'summary': "Stock Barcode Customization",

    'description': """
        Stock Barcode
    """,

    'author': "Captivea",
    'website': "https://www.captivea.com",

    'version': '0.1',
    'depends': ['product_multi_barcode','product'],

    # always loaded
    'data': [
        'views/stock_product_selector.xml',
        'report/product_barcode.xml',
        'report/report_deliveryslip.xml',
        'wizard/product_label_layout.xml',
        'views/stock_picking_type.xml',
        'views/stock_picking.xml'
    ],
     'assets': {
        'web.assets_backend': [
            'cap_stock_barcode/static/src/**/*.js',
            'cap_stock_barcode/static/src/*.js',
            'cap_stock_barcode/static/src/**/*.xml',
        ],

    }
}

