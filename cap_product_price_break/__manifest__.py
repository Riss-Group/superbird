# -*- coding: utf-8 -*-
{
    'name': 'CAP Sale Price Breakdown',
    'category': 'Sales',
    'summary': "CAP Sale Price Breakdown",
    'version': '1.0',
    'author': 'Captivea software Consulting, Kevin Lai',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
This module contains customizations for common sales features.
        """,
    'depends': [
        'sale',
        'website_sale',
        'sale_product_configurator',
    ],
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            'cap_product_price_break/static/src/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
