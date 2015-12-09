# coding: utf-8
{
    "name": "MRP Workcenter Account Move",
    "version": "1.0",
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
    ],
    "demo": [
        'demo/demo.xml',
    ],
    "data": [
        'view/view.xml',
        'view/wizard.xml',
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "external_dependencies": {
    }
}
