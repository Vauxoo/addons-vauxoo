# -*- coding: utf-8 -*-

{
    "name": "Landed Costs for Avarage Costing Method",
    "version": "8.0.1.1.0",
    "author": "Vauxoo",
    "category": "Generic Modules/Account",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "account",
        "stock_landed_costs",
        "stock_deviation_account",
        "purchase",
        "mrp",
        "stock_card",
    ],
    "demo": [
        "demo/account_invoice_demo.xml",
    ],
    "data": [
        "view/stock_landed_costs.xml",
        "view/account_invoice.xml",
    ],
    "installable": True,
    "auto_install": False,
}
