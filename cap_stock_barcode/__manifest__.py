# -*- coding: utf-8 -*-
{
    'name': "cap stock barcode",

    'summary': "Stock Barcode Customization",

    'description': """
        Stock Barcode
    """,

    'author': "Captivea",
    'website': "https://www.captivea.com",

    'version': '0.1',
    'depends': ['stock_barcode','product'],

    # always loaded
    'data': [
        'views/stock_product_selector.xml',
        'report/product_barcode.xml',
        'wizard/product_label_layout.xml'
    ],
     'assets': {
        'web.assets_backend': [
            'cap_stock_barcode/static/src/**/*.js',
            'cap_stock_barcode/static/src/**/*.xml',
        ],

    }
}

