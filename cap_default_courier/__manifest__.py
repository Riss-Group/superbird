{
    'name': 'cap_default_courier',
    'version': '1.0',
    'category': 'Contacts',
    'summary': 'A new Odoo module',
    'depends': [
        'base',
        'contacts',
        'delivery',
        ],
    'data': [
        'views/menuitems.xml',
        'views/res_partner.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
