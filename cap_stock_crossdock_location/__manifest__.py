# -*- coding: utf-8 -*-
{
    'name': "cap_stock_crossdock_location",

    'summary': "Cross-Dock location",

    'description': """
        Cross-Dock location
    """,

    'author': "Captivea CA",
    'website': "https://www.captivea.com",
    'category': 'stock',
    'version': '1.0',
    'depends': ['stock'],
    # always loaded
    'data': [
        'views/stock_warehouse.xml',
        'views/stock_picking_type.xml',
    ],

}

