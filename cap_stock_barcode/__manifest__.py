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
        'report/product_barcode.xml'
    ],
     'assets': {
        'web.assets_backend': [
            'cap_stock_barcode/static/src/**/*.js',
            'cap_stock_barcode/static/src/**/*.xml',
        ],

    }
}

