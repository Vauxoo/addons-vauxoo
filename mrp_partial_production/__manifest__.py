# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "MRP Partial Production",
    "version": "saas-17.0.0.1.0",
    "author": "Vauxoo",
    "category": "",
    "website": "http://www.vauxoo.com/",
    "license": "LGPL-3",
    "depends": [
        "sale_stock",
        "mrp",
    ],
    "demo": [
        'demo/product_demo.xml',
        'demo/stock_demo.xml',
        'demo/mrp_bom_demo.xml',
        'demo/sale_demo.xml',
    ],
    "data": [
        'views/mrp_view.xml',
    ],
    "installable": True,
    "auto_install": False,
}
