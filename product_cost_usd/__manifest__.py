# -*- coding: utf-8 -*-
# Copyright 2017 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Product Price Cost in USD",
    "summary": '''
This module adds the field Cost in USD to the Product form.
    ''',
    "version": "10.0.0.0.1",
    "author": "Vauxoo",
    "category": "Rico",
    "website": "http://vauxoo.com",
    "license": "LGPL-3",
    "depends": [
        'product',
        'sale_margin',
    ],
    "demo": [
    ],
    "data": [
        "views/product_view.xml",
    ],
    "test": [],
    "installable": True,
    "auto_install": False,
}
