# -*- coding: utf-8 -*-
{
    'name': "Sales Product Restrictions",

    'summary': "Sales Product Restrictions",

    'description': """
        Sales Product Restrictions
    """,

    'author': "Captivea Canada",
    'website': "https://www.captivea.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_restriction_view.xml',
        'views/sale.xml',
    ],
}

