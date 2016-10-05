# coding: utf-8
{
    "name": "Stock Card",
    "version": "8.0.2.0.0",
    "author": "Vauxoo",
    "category": "Tools",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "account",
        "base",
        "stock",
        "purchase",
        "sale",
    ],
    "demo": [
        'demo/demo.xml',
    ],
    "data": [
        'security/ir.model.access.csv',
        'view/view.xml',
        'view/wizard.xml',
    ],
    "installable": True,
    "auto_install": False,
    'external_dependencies': {
        'bin': [],
        'python': [
            'tabulate',
            'pandas',
        ],
    }
}
