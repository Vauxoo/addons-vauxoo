{
    "name": "Account Currency Tools",
    "version": "12.0.1.0.0",
    "author": "Vauxoo",
    "category": "Tools",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "base",
        "account",
    ],
    "data": [
        'views/res_company_views.xml',
        'wizards/exchange_realization.xml',
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "external_dependencies": {
        "python": [
            'pandas'
        ]
    }
}
