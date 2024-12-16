# -*- coding: utf-8 -*-
{
    'name': 'CAP Stock Picking Assignment',
    'category': 'Inventory/Inventory',
    'summary': "CAP stock picking assignment",
    'version': '17.0.0.0',
    'author': 'Captivea software Consulting',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        """,
    'depends': [
        'stock'
        ],
    'data': [
        'views/stock_warehouse_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
