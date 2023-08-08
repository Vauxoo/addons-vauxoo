{
    "name": "Internal transfers with an agreed amount",
    "version": "12.0.1.0.0",
    "author": "Vauxoo",
    "website": "http://www.vauxoo.com/",
    "license": "LGPL-3",
    "category": "account",
    "depends": [
        "account",
    ],
    "data": [
        # Security
        "security/res_groups_security.xml",
        # Wizards
        "wizards/internal_transfer_multicurrency_views.xml",
        # Views
        "views/account_payment_views.xml",
    ],
    "installable": True,
}
