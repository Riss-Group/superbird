# -*- coding: utf-8 -*-
{
    'name': "CAP Product Configurator",
    'summary': "CAP Product Configurator",
    'license': 'OPL-1',
    'description': """
    TBD
    """,
    'author': 'Captivea software Consulting',
    'website': 'https://www.captivea.com/',
    'category': 'Uncategorized',
    'version': '1.0',
    'depends': ['product_configurator_sale','stock'],

    # always loaded
    'data': [
        'wizard/product_configurator.xml',
        'views/product_attribute_views.xml',
    ],

}

