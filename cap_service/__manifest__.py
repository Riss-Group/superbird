# -*- coding: utf-8 -*-
{
    'name': 'CAP Service',
    'category': 'Service',
    'summary': "CAP Service",
    'version': '1.0',
    'author': 'Captivea software Consulting, Bassim Elsamaloty',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        TBD
        """,
    'depends': ['account', 'sale', 'stock', 'fleet', 'product', 'project', 'timesheet_grid'],
    'data': [
        'data/sequence.xml',
        'report/sale_report_views.xml',
        'security/ir.model.access.csv',
        'views/_menus_actions.xml',
        'views/fleet_vehicle.xml',
        'views/project_task.xml',
        'views/sale_order.xml',
        'views/service_order.xml',
        'views/service_ccc.xml',
        'wizard/service_line_view_product.xml',
        'wizard/service_template_select.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}