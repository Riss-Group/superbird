# -*- coding: utf-8 -*-
{
    'name': "cap helpdesk stock",
    'license': 'OPL-1',

    'summary': "This module customize Helpdesk RMA",

    'description': """
        This module customize Helpdesk RMA
    """,

    'author': "Captivea Canada",
    'website': "https://www.captivea.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['helpdesk_stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_return.xml',
        'views/helpdesk_team.xml',
        'views/stock_return_reason.xml',
    ],

}

