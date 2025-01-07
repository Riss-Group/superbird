{
    'name': 'cap_account_distribution',
    'version': '1.0',
    'license': 'OPL-1',
    'category': 'Accounting',
    'summary': 'Adds smart button(s) to the Journal Entry form view to allow for redistribution of amounts across severl accounts. Allows for configuration of each account for this functionality.',
    'depends': [
        'base',
        'account',
        'account_accountant',
        ],
    'data': [
        'views/account_account.xml',
        'views/account_move.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
