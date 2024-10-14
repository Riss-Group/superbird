# -*- coding: utf-8 -*-
{
    'name': 'CAP Sale',
    'category': 'Sales',
    'summary': "CAP Sale",
    'version': '1.0',
    'author': 'Captivea software Consulting, Kevin Lai',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
This module contains customizations for common sales features.
        """,
    'depends': [
        'sale',
        ],
    'data': [
        'views/product_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}