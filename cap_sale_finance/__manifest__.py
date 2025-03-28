# -*- coding: utf-8 -*-
{
    'name': 'CAP Sale Finance',
    'category': 'Sales',
    'summary': "Financing Options for Sales",
    'version': '1.1',
    'author': 'Captivea software Consulting, Bassim Elsamaloty',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        - Adds a new table under the sales order for financing calculations
        """,
    'depends': [
        'sale', 'base',
        ],
    'external_dependencies': {
        'python': ['numpy-financial']
    },
    'data': [
        'security/ir.model.access.csv',
        'security/sale_finance_terms_security.xml',
        'views/sale_order_views.xml',
        'views/res_partner_views.xml',
        'views/sale_finance_terms_views.xml',
        'reports/sale_finance_report_inherit.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}