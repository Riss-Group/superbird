{
    'name': 'AI Purchase Order Digitalization (OCR)',
    'version': '17.0.0.0',
    'category': 'Extra Tools',
    'summary': """Digitize Invoices,
    """,
    'description': """
        This module allows users to digitize invoices, extract relevant information using OCR, and complete Odoo records
         with the extracted data also using artificial intelligence.
    """,
    'author': "David Montero Crespo",
    'website': 'https://odoonext.com',
    'depends': ['purchase'],
    'external_dependencies': {
        'python': ['pytesseract', 'pypdf', 'pdf2image', 'numpy', 'Pillow', 'fuzzywuzzy'],
    },
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_digitalize.xml',
        'views/purchase_order.xml',
    ],
    'installable': True,
    'application': True,
    'price': 125,
    'auto_install': False,
    'license': 'AGPL-3',
    "images": ["static/ai_completion.gif"],
}
