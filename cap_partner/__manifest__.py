# -*- coding: utf-8 -*-
{
    'name': 'CAP Partner',
    'category': 'Partner',
    'summary': "CAP Partner",
    'version': '1.0',
    'author': 'Captivea France (North), Stalmarski Marvyn',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        - Add Custom Contact type in partner
        """,
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
