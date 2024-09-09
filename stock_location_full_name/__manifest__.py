# -*- coding: utf-8 -*-
{
    'name': 'Stock Location Full Name',
    'category': 'Inventory',
    'summary': "Set Location full name as the concatenation of the parent locations regardless of the parent views type",
    'version': '1.0',
    'author': 'Captivea',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        """,
    'depends': [
        'stock',
        ],
    'data': [
        'views/stock_warehouse_views.xml',
    ],
}