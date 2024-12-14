# -*- coding: utf-8 -*-
{
    'name': 'CAP Sale Purchase Legacy',
    'category': 'Hidden',
    'summary': "CAP Sale Purchase Legacy",
    'version': '1.0',
    'author': 'Captivea software Consulting',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'sequence': 500,
    'description': """
        """,
    'depends': [
        'sale_stock',
        'purchase',
        ],
    'data': [
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
