# coding: utf-8
{
    "name": "Account Reconcile Advance",
    "version": "8.0.0.1.6",
    "author": "Vauxoo",
    "category": "Generic Modules",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "account",
        "account_voucher"
    ],
    "demo": [],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "view/view.xml",
        "view/menues_and_actions.xml"
    ],
    "test": [
        "test/advance_greater_than_payment.yml",
        "test/advance_less_than_payment.yml",
        "test/advance_equals_than_payment.yml",
        "test/advance_greater_than_payment_customer.yml",
        "test/advance_less_than_payment_customer.yml",
        "test/advance_equals_than_payment_customer.yml"
    ],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
}
