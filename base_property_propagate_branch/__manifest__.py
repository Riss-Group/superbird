# -*- coding: utf-8 -*-
{
    'name': 'Base Property Propagate Branch',
    'version': '17.0.1.0.0',
    'author': 'Captivea',
    'website': 'https://www.captivea.com',
    'category': 'Technical',
    'summary': 'Propagates company-dependent fields to other branches of the same company.',
    'description': """
Override BaseModel.write to propagate changes in specific fields to other branches.
    """,
    'depends': ['base_setup'],
    'data': [
        'views/res_config_settings_views.xml'
    ],
    'installable': True,
    'license': 'AGPL-3',
}