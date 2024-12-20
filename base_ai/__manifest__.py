{
    'name': 'AI Integration',
    'version': '17.0.0.1',
    'category': 'Extra Tools',
    'license': 'OPL-1',
    'summary': "AI integration base module allowing OCR and ChatGPT integration",
    'author': "Captivea",
    'website': 'https://www.captivea.com',
    'depends': ['base_setup', 'web'],
    'external_dependencies': {
        'python': [
            'pytesseract',
            'pdf2image',
            'openai',
            'requests',
            'boto3'
        ],
    },
    'data': [
        'views/ir_model_views.xml',
        'views/ai_model_config_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/base_digitalize_wizard_views.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'base_ai/static/src/js/*',
            'base_ai/static/src/components/**/*',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
    "images": ["static/ai_completion.gif"],
}
