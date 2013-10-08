# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Jorge Angel Naranjo (jorge_nr@vauxoo.com)
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
{
    "name": "Purchase Test Data IMP",
    "version": "1.0",
    "depends": [
        "base",
        "purchase",
        "account",
        "product",
        "stock",
    ],
    "author": "Vauxoo",
    "description": """
Purchase Test Data IMP
======================

This test yaml validate that data of products is correct.

Creating a purchase order, picking in and supplier invoice by product.
    """,
    "website": "http://vauxoo.com",
    "category": "Addons Vauxoo",
    "demo": [],
    "test": [
                 'test/purchase_order_test_data.xml',
                 'test/purchase_order_product_can_be_purchased.yml', ],
    "data": [
                'wizard/wizard.xml',
            ],
    "active": False,
    "installable": True,
}
