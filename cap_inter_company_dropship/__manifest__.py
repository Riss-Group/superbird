# -*- coding: utf-8 -*-
{
    'name': "cap inter company dropship",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Captivea CA",
    'website': "https://www.captivea.com",

    'category': 'Inventory/Inventory',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['stock_dropshipping','sale_order_global_stock_route'],

    # always loaded
    'data': [
        'views/stock_route.xml',
    ],

}

