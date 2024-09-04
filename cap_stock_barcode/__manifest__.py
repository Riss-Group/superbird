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
    'depends': ['stock_barcode'],

    # always loaded
    'data': [

    ],
     'assets': {
        'web.assets_backend': [
            'cap_stock_barcode/static/src/**/*.js',
        ],

    }
}

