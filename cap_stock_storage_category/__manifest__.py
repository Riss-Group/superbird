# -*- coding: utf-8 -*-
{
    'name': "cap stock storage category",

    'summary': "Storage Category",

    'description': """
        Storage Category
    """,

    'author': "Captivea",
    'website': "https://www.captivea.com",

    'version': '0.1',
    'depends': ['stock'],

    # always loaded
    'data': [
        'views/stock_location_views.xml',
        'views/stock_storage_category_views.xml',
        'views/stock_putaway_rule_views.xml',
        'views/product_template_views.xml',
        'security/ir.model.access.csv'
    ],
}

