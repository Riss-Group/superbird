# -*- coding: utf-8 -*-
{
    'name': 'CAP Service Extended',
    'category': 'Service',
    'summary': "CAP Service Extended",
    'version': '17.0.0.0.0',
    'author': 'Captivea software Consulting',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        """,
    'depends': [
        'cap_service',
    ],
    'data': [
        'views/fleet_vehicle_views.xml',
        'views/fleet_vehicle_model_views.xml',
        'views/stock_picking_views.xml',
        'views/fleet_vehicle_manufacturer_chassis_views.xml',
        'views/fleet_vehicle_engine_views.xml',
        'views/fleet_vehicle_transmission_views.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': False,
}