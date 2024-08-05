# -*- coding: utf-8 -*-
{
    'name': 'CAP Stock',
    'category': 'Inventory',
    'summary': "CAP Stock",
    'version': '1.0',
    'author': 'Captivea software Consulting, Bassim Elsamaloty',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        - Adds the ability to use custom formulas within reordering rules
        """,
    'depends': [
        'stock',
        ],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/_menu_actions.xml',
        'views/reordering_rule_python_code.xml',
        'views/stock_warehouse.xml',
        'views/stock_warehouse_orderpoint.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}