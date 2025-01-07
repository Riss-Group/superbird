# -*- coding: utf-8 -*-
{
    'name': 'CAP Default Courier',
    'version': '1.0',
    'license': 'OPL-1',
    'category': 'Contacts',
    'summary': 'A new Odoo module',
    'depends': [
        'base',
        'contacts',
        'delivery',
        ],
    'data': [
        'views/delivery_carrier_views.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
    'application': False,
}
