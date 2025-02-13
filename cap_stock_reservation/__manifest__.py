# -*- coding: utf-8 -*-
{
    'name': "cap stock reservation",
    'license': 'OPL-1',

    'summary': "CAP Stock reservation",

    'description': """
        CAP Stock Reservation
    """,

    'author': "Captivea",
    'website': "https://www.captivea.com",

    'version': '0.1',
    'depends': ['stock_barcode'],

    # always loaded
    'data': [
        'views/stock_picking_type.xml',
        'views/stock_location.xml',
    ],
     'assets': {
        'web.assets_backend': [
            'cap_stock_reservation/static/src/**/*.js',
            'cap_stock_reservation/static/src/**/*.xml',
        ],

    }
}

