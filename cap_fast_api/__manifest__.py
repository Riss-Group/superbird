# -*- coding: utf-8 -*-
{
    'name': 'CAP Fast API',
    'category': 'Technical',
    'summary': "CAP Fast API Extended",
    'version': '1.1',
    'author': 'Captivea software Consulting, Bassim Elsamaloty',
    'website': 'https://www.captivea.com/',
    'license': 'OPL-1',
    'description': """
        Adds capability to submit FastAPI requests through Odoo with external_ids
        **WARNING**
        This app needs most likely needs to be installed via CLI since it adds a field to all base models to be used in external ID processing 
        """,
    'depends': [
        'fastapi',
        'purchase',
        'account',
        'sale',
        'delivery'
    ],
    'data': [
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/fastapi_company_map.xml",
        "views/fastapi_endpoint.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}