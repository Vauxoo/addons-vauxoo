# coding: utf-8
{
    "name": "MRP Workcenter Account Move",
    "version": "8.0.1.0.0",
    "author": "Vauxoo",
    "category": "Tools",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "base",
        "account",
        "mrp",
        "account_move_line_production",
        "stock_card",
        "mrp_routing_account_journal",
        "stock_deviation_account",
    ],
    "demo": [
        'demo/demo.xml',
    ],
    "data": [
        'view/view.xml',
        'view/wizard.xml',
    ],
    "installable": True,
    "auto_install": False,
}
