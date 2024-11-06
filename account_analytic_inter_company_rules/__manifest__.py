# -*- coding: utf-8 -*-
{
    "name": "Inter Company Module for Invoices Analytic",
    "version": "17.0.0.0.0",
    "summary": "Intercompany INV rules",
    "category": "Productivity",
    "description": """
    Module splits invoice lines by analytics if interco automation is selected
    """,
    "depends": ["account_inter_company_rules"],
    "data": [
        "views/account_move_views.xml",
        "views/analytic_account_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
