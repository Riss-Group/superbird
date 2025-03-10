# -*- coding: utf-8 -*-
{
    'name': 'CAP Contact Tax Configuration',
    'category': 'Uncategorized',
    'summary': "CAP Contact Tax Configuration",
    'version': '1.0',
    'author': 'Captivea software Consulting',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        """,
    'depends': [
        'base', 'account', 'l10n_ca'
        ],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'data/email_template.xml',
        'views/account_fiscal_position_views.xml',
        'views/rec_config_settings_views.xml',
        'views/rec_partner_views.xml',
        'views/tax_exempt_reason_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
