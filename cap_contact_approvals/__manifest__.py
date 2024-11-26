{
    'name': 'cap_contact_approvals',
    'version': '1.0',
    'category': 'Uncategorized',
    'summary': 'A new Odoo module',
    'depends': ['base','contacts','approvals'],
    'data': [
        'data/approval_category.xml',
        'views/approval_request.xml',
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
