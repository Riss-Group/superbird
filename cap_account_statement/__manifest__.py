# -*- coding: utf-8 -*-
{
    'name': 'CAP Account Statements',
    'category': 'Accounting',
    'summary': "CAP Account Statements",
    'version': '1.0',
    'author': 'Captivea software Consulting, Bassim Elsamaloty',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        - Introduces partner statements 
        """,
    'depends': [
        'account', 
        'account_followup',
        ],
    'data': [
        'data/data.xml',
        'report/customer_statement.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}