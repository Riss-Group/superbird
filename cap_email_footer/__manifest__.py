{
    'name': 'cap_email_footer',
    'version': '1.0',
    'category': 'Email',
    'summary': 'Dynamic Email Footer dictated by department, module, and/or domain that the record is being printed from.',
    'depends': [
        'base',
        ],
    'data': [
        'views/res_company.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
