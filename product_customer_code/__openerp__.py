# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) info@vauxoo.com
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Products Customer Code",
    "version": "8.0.0.1.7",
    "author": "Vauxoo",
    "category": "Generic Modules/Product",
    "website": "http://www.vauxoo.com/",
    "license": "LGPL-3",
    "depends": [
        "base",
        "product"
    ],
    "demo": [],
    "data": [
        "security/product_customer_code_security.xml",
        "security/ir.model.access.csv",
        "views/product_customer_code_view.xml",
        "views/product_product_view.xml"
    ],
    "test": [],
    "installable": True,
    "auto_install": False,
}
