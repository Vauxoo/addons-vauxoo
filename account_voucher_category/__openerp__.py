# -*- encoding: utf-8 -*-
{
    "name": "Account Voucher Category", 
    "version": "1.0", 
    "author": "Vauxoo", 
    "category": "Generic Modules", 
    "description": """
Account Voucher Category
========================

This module adds a field into account.voucher module that will later be used
to write into the Entry Lines of the account Bank Journal, Afterwards this field
will be used to create a new kind of reports related to Cash Flow.
    """, 
    "website": "http://www.vauxoo.com/", 
    "license": "AGPL-3", 
    "depends": [
        "account_voucher"
    ], 
    "demo": [], 
    "data": [
        "security/ir.model.access.csv", 
        "view/view.xml", 
        "view/menues_and_actions.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: