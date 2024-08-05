# -*- coding: utf-8 -*-
{
    'name': 'Chart Of Accounts Enhancement',
    'category': 'Accounting',
    'summary': "Adds Parent COA functionality",
    'version': '1.5',
    'author': 'Captivea software Consulting, Bassim Elsamaloty',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        Creates top level COA.
        Streamlines the administration of account.accounts
        """,
    'depends': [
        'account', 
        'account_accountant' ],
    'data': [
        'security/ir.model.access.csv',
        'views/_menus_actions.xml',
        'views/account_account_template.xml',
        'views/account_account.xml',
        'views/res_company.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}