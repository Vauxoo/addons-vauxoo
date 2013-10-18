# -*- encoding: utf-8 -*-
{
    "name": "Account Move Folio",
    "version": "1.0",
    "author": "Vauxoo",
    'category' : 'Accounting & Finance',
    "description" : """
Account Move Folio
==================

This Module keeps a record of all the sequences that have been used in the
Journal Entries in OpenERP, No matter if a Journal Entry is deleted it will
stand as a way to audit all the sequences that have been used.
    """,
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
            "account",
                ],
    "demo": [
    ],
    "data": [
        'security/ir.model.access.csv',
        'view/view.xml',
        'view/menues_and_actions.xml',
    ],
    "test" : [
    ],
    "installable": True,
    "active": False,
}
