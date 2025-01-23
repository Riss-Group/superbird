# -*- coding: utf-8 -*-
{
    'name': 'CAP Purchase Quality Check',
    'category': 'Uncategorized',
    'summary': "CAP Purchase Quality Check",
    'version': '17.0.0.0.1',
    'author': 'Captivea software Consulting',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        """,
    'depends': [
        'quality_control', 'purchase',
        ],
    'data': [
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
