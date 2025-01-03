# -*- coding: utf-8 -*-
{
    "name": "Payment Term Multi-Company",
    "summary": "Select payment term for multiple company",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["base_multi_company","account"],
    "author": "Captivea CA",
    "category": "Invoices & Payments",
    "data": [
        'security/access_right_security.xml',
        'views/account_payment_term_views.xml'
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "post_init_hook": "post_init_hook",
}
