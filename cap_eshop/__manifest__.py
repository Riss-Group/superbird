{
    'name': "CAP - SUPERBIRD Eshop",
    'summary': "SUPERBIRD Eshop Customization",
    'description': """
        A custom module to custom Eshop
    """,
    'version': '1.1',
    'author': 'captivea-rojo',
    'depends': ['emipro_theme_base','website_sale'],
    'data': [
        'views/custom_templates.xml',
        'views/website_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'cap_eshop/static/src/scss/styles.scss',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
