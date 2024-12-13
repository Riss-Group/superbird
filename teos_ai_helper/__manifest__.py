{
    'name': 'TEOS AI Helper',
    'author': 'TEOS Tangier',
    'category': 'Custom',
    'website': 'https://teos.odoo.com/',
    'license': 'AGPL-3',
    'summary': "TEOS AI Helper",
    "version": "17.0.1.1.2",
    'description': """
    """,
    'depends': [
        'base_setup',
        'web_editor',
        'mail'
    ],
    'data': ['views/res_config_settings_views.xml',
             'security/base_groups.xml'],
    'assets': {
        'web.assets_backend': [
            'teos_ai_helper/static/src/ai_helper/chatgpt_prompt_dialog.js',
            'teos_ai_helper/static/src/ai_helper/ai_helper_menu.js',
            'teos_ai_helper/static/src/ai_helper/ai_help_menu.xml',
            ('include', 'web_editor.backend_assets_wysiwyg'),
        ],
        'web_editor.assets_wysiwyg':
            ['teos_ai_helper/static/src/ai_helper/ai_prompt_dialogue.xml'],
        'web._assets_core': [
            'teos_ai_helper/static/src/ai_helper/user_service.js',
        ],
    },
    'images': ['static/description/gif_demo.gif'],
    'installable': True,
}
