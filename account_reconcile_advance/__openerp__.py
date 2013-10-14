# -*- encoding: utf-8 -*-
{
    "name": "Account Reconcile Advance",
    "version": "1.0",
    "author": "Vauxoo",
    "category": "Generic Modules",
    "description" : """
Account Reconcile Advance
=========================

A description is intended to fill this space
    """,
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
            "account",
            "account_voucher",
                ],
    "demo": [
    ],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'view/view.xml',
        'view/menues_and_actions.xml',
    ],
    "test" : [
            "test/advance_greater_than_payment.yml",
            "test/advance_less_than_payment.yml",
            "test/advance_equals_than_payment.yml",
            "test/advance_greater_than_payment_customer.yml",
            "test/advance_less_than_payment_customer.yml",
            "test/advance_equals_than_payment_customer.yml",
    ],
    "installable": True,
    "active": False,
}
