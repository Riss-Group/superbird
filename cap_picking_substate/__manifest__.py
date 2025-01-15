{
    'name': 'Picking Substate',
    'version': '1.0.0',
    'summary': 'Manage substates in stock picking operations',
    'description': """
        This module adds a custom substate field to the stock picking model
        to help track the progress of picking operations more granularly.
    """,
    'author': 'Captivea',
    'website': 'http://captivea.com',
    'category': 'Warehouse',
    'depends': ['base_substate', 'stock'],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
}