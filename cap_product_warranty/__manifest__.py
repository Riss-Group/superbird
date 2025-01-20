# -*- coding: utf-8 -*-
{
    'name': "cap_product_warranty",

    'summary': "Product Warranty Expiration Date",

    'description': """
        Product Warranty Expiration Date
    """,

    'author': "Captivea CA",
    'website': "https://www.captivea.com",
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['product_warranty'],

    # always loaded
    'data': [
        'views/stock_move.xml',
    ],

}

