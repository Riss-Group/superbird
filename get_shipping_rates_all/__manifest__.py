# -*- coding: utf-8 -*-

{
    'name': 'Get All Shipping Cost',
    'version': '1.0',
    'summary': """This module fetch all shipping method rates while adding shipping to sale order. then you review all shipping rate and select less cheaper rates..
""",
    "description": """
    all shipping cost.
    list all shipping cost.
    all delivery method cost.
    list all delivery method cost.
    all shipping rate sale order.
    show all shipping rate on sale order.
    fetch all shipping method delivery cost.
    fetch all delivery method cost.
    all shipping method cost.
    get rate of all shipping method.
""",
    'author': 'Valueble IT Solution',
    'company': 'Valueble IT Solution',
    'website': 'valuebleitsolution.odoo.com',
    'price': "60",
    'currency': 'USD',
    'license': 'AGPL-3',
    'images': ['static/description/image4.png'],
    'depends': ['base', 'sale', 'delivery'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/delivery_carrier.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
}
