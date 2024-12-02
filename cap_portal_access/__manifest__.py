# -*- coding: utf-8 -*-
{
    'name': 'Manage Portal Access',
    'version': '17.0.0.1',
    'summary': 'Portal Access Management',
    'description': """Helps To Manage Portal Access""",
    'category': '',
    'depends': ['base', 'sale', 'project', 'account', 'hr_timesheet', 'portal'],
    'data': [
        'views/res_partner_inherit_views.xml',
        'views/portal_templates.xml',
        'wizard/portal_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
