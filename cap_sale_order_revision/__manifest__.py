{
    'name': 'CAP Sale Order Revision',
    'version': '17.0.0.0',
    'category': 'Sale',
    'license': 'OPL-1',
    'summary': 'Module sale_order_revision extended',
    'depends': [
        'sale_order_revision',
        'sale_crm',
        'sale_stock',
        ],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
