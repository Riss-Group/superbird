# -*- coding: utf-8 -*-
{
    'name': "cap product core type",
    'license': 'OPL-1',

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Captivea CA",
    'website': "https://www.captivea.com",

    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_stock', 'purchase_stock','cap_pricelist'],

    # always loaded
    'data': [
        'data/core_part_data.xml',
        'views/products.xml',
        'views/sale.xml',
    ],
}

