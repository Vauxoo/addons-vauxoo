{
    "name": "Account Bank Reconcile Transfer",
    "summary": """Create bank transfers directly from the bank reconciliation screen.""",
    "author": "Vauxoo",
    "website": "https://www.vauxoo.com",
    "license": "LGPL-3",
    "category": "Accounting/Accounting",
    "version": "15.0.1.0.0",
    "depends": [
        "account_accountant",
    ],
    "data": [],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "account_bank_reconcile_transfer/static/src/js/bank_reconciliation.js",
        ],
        "web.assets_qweb": [
            "account_bank_reconcile_transfer/static/src/xml/bank_reconciliation.xml",
        ],
    },
    "installable": True,
}
