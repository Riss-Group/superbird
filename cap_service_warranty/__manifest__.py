# -*- coding: utf-8 -*-
{
    'name': 'CAP Service Warranty',
    'category': 'Service',
    'summary': "CAP Service Warranty",
    'version': '17.0.0.0.0',
    'author': 'Captivea software Consulting',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        """,
    'depends': [
        'cap_service', 'sale_stock'
    ],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/service_order_views.xml',
        'views/warranty_claim_views.xml',
        'views/stock_warehouse_views.xml',
        'wizard/warranty_claim_return_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
