{
    'name': 'cap_crm_advance',
    'version': '1.0',
    'category': 'CRM',
    'license': 'OPL-1',
    'summary': 'Proposition Stage management and Automatically pushing advancing a lead into the Proposition stage',
    'depends': [
        'base',
        'crm',
        'sale',
        ],
    'data': [
        'views/crm_lead.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
