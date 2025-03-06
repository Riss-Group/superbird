{
    'name': "CAP - SUPERBIRD Eshop",
    'summary': "SUPERBIRD Eshop Customization",
    'description': """
        A custom module to custom Eshop
    """,
    'version': '1.1',
    'author': 'captivea-rojo',
    'depends': ['website_sale','emipro_theme_base'],
    'data': [
        'views/custom_templates.xml',
        'views/website_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'cap_eshop/static/src/scss/styles.scss',
            'cap_eshop/static/src/js/js_functions.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
