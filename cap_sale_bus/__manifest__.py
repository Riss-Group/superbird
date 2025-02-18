# -*- coding: utf-8 -*-
{
    'name': 'CAP Bus Sale',
    'category': 'Sales',
    'summary': "CAP Sale",
    'version': '1.0',
    'author': 'Captivea software Consulting',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
This module contains customizations for common sales features.
        """,
    'depends': [
        'cap_service',
        ],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
}
