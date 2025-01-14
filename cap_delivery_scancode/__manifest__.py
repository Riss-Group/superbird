# -*- coding: utf-8 -*-
{
    'name': 'CAP Delivery Scancode',
    'category': 'Inventory/Delivery',
    'summary': "Send your parcels through Scancode and track them online",
    'version': '1.0',
    'author': 'Captivea software Consulting',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        """,
    'depends': [
        'stock_delivery', 'mail', 'get_shipping_rates_all'
        ],
    'data': [
        'views/res_config_settings_views.xml',
        'views/delivery_carrier_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
