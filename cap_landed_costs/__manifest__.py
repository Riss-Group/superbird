# -*- coding: utf-8 -*-
{
    'name': 'CAP Landed Costs',
    'category': 'Accounting',
    'summary': "CAP Landed Costs",
    'version': '1.0',
    'author': 'Captivea software Consulting, Bassim Elsamaloty',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        - Automates the assigning of landed costs via estimates
        """,
    'depends': [
        'account', 
        'product', 
        'purchase',
        'stock_landed_costs',
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/product.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}