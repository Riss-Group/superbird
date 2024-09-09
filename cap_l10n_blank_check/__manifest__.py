# -*- coding: utf-8 -*-
{
    'name': 'CAP Check Printing',
    'category': 'Accounting',
    'summary': "CAP Check Printing",
    'version': '1.0',
    'author': 'Captivea software Consulting, Bassim Elsamaloty',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        - Adds a new blank check layout
        """,
    'depends': [
        'account_check_printing',
        ],
    'data': [
        'data/data.xml',
        'views/account_journal.xml',
        'report/print_check.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'cap_l10n_blank_check/static/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}