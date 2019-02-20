# coding: utf-8
{
    "name": "Website Product Availability",
    "version": "8.0.0.1.6",
    "author": "Vauxoo",
    "category": "Website",
    "website": "http://www.vauxoo.com/",
    "license": "LGPL-3",
    "depends": [
        "stock",
        "purchase",
        "website_sale",
    ],
    "demo": [
        "demo/stock_alias.xml",
        "demo/purchase_order.xml",
    ],
    "data": [
        # "views/layout.xml",
        # "views/templates.xml",
        # "views/product_view.xml",
        "security/stock_quant.xml",
        "security/ir.model.access.csv",
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [
    ],
    "installable": True,
    "auto_install": False,
}
