# -*- coding: utf-8 -*-
{
    'name': "CAP Pricelist",
    'license': 'OPL-1',

    'summary': "Customize Pricelist",

    'description': """
        Add Lowest Price Option  
        add Pricelist rule by ecommerce category / vendor  
        """,

    'author': "Captivea CANADA",
    'website': "https://www.captivea.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_sale'],

    # always loaded
    'data': [
        'views/product_pricelist_item_view.xml',
        'views/product.xml',
    ],
}

