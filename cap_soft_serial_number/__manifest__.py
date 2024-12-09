# -*- coding: utf-8 -*-
{
    'name': "Soft Serial Number",

    'summary': "Soft Serial Number",

    'description': """
Long description of module's purpose
    """,

    'author': "Captivea CA",
    'website': "https://www.captivea.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['stock_barcode','sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template.xml',
        'views/stock_product_selector.xml',
        'views/account_move.xml',
    ],

}

