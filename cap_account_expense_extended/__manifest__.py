# -*- coding: utf-8 -*-
{
    'name': 'CAP Account Expense Extended',
    'category': 'Accounting',
    'summary': "CAP Account Expense",
    'version': '1.0',
    'author': 'Captivea software Consulting',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        - Create an expense from the bank statement. based on the employee configure on the journal
        """,
    'depends': [
        'account', 'hr_expense',
        ],
    'data': [
        'views/account_journal_views.xml',
        'views/hr_expense_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
