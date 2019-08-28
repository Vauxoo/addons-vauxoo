# -*- coding: utf-8 -*-
# Copyright 2019 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Product Sale Price in USD",
    "summary": '''
This module adds the field Sale Price in USD to the Product form.
    ''',
    "version": "10.0.0.0.1",
    "author": "Vauxoo",
    "category": "Sales",
    "website": "http://vauxoo.com",
    "license": "LGPL-3",
    "depends": [
        'product',
        'sale',
    ],
    "data": [
        "views/product_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
