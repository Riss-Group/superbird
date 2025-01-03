# -*- coding: utf-8 -*-
{
    'name': 'Custom CRM Module',
    'category': 'CRM',
    'summary': "Add all customs for crm",
    'version': '1.5',
    'author': 'Captivea France (North) - Stalmarski Marvyn',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        Add RFQ Unique Reference
        """,
    'depends': [
        'crm',
        'sale',
        'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
