# -*- coding: utf-8 -*-
{
    'name': 'CAP Common Library',
    'category': 'Productivity',
    'summary': "CAP Common Library",
    'version': '0.3',
    'author': 'Captivea software Consulting, Bassim Elsamaloty',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        - Generic fields and views required for the project.
        """,
    'depends': [
        'base',
        'account',
        ],
    'data': [
        'security/ir.model.access.csv',
        'data/available_days_data.xml',
        'views/contact.xml',
        'views/product.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}