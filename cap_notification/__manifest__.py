# -*- coding: utf-8 -*-
{
    'name': "cap notification",

    'summary': "Add the parameter to set the time the warnings get displayed",

    'description': """
        Add the parameter to set the time the warnings get displayed
    """,

    'author': "Captivea, AS",
    'website': "https://www.captivea.com",
    'version': '0.1',
    'depends': ['web'],

    # always loaded
    'data': [
        "data/data.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'cap_notification/static/src/*.js',
        ],
    }

}

