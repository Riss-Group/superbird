{
    'name': 'AI Integration',
    'version': '17.0.1.1',
    'category': 'Extra Tools',
    'license': 'OPL-1',
    'summary': "AI Accounting integration base module allowing OCR and ChatGPT integration",
    'author': "Captivea",
    'website': 'https://www.captivea.com',
    'depends': ['base_ai', 'account'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
