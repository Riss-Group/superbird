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
        # 'account',
        # 'sale',
        # 'stock',
        # 'fleet',
        # 'purchase',
        # 'product',
        # 'project',
        # 'quality_control' ,
        # 'sale_planning',
        # 'sale_renting',
        # 'sale_renting_sign',
        # 'project_forecast',
        # 'timesheet_grid'
    ],
    'data': [
        'views/fleet_vehicle_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}