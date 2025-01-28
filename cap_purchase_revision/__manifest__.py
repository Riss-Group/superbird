{
    'name': 'cap_purchase_revision',
    'version': '1.0',
    'category': 'Purchase',
    'license': 'OPL-1',
    'summary': 'When cancelling a Purchase order we allow the user to create a Revision of the current Purchase Order.',
    'depends': [
        'base',
        'purchase',
        'purchase_stock',
        'purchase_requisition',
        ],
    'data': [
        'data/mail_template_chatter.xml',
        'views/purchase_order.xml',
    ],
    'installable': True,
    'application': False,
}
