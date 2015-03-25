# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
#
#    Coded by: Jorge Angel Naranjo Rogel (jorge_nr@vauxoo.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
{
    "name": "Validate Stock Move Product", 
    "version": "1.0", 
    "author": "Vauxoo", 
    "category": "Addons Vauxoo", 
    "description": """
Validate Stock Move Product
===========================

This module validates the quantity of product to be moved to
destination location in the source location exists. If you do
not have the amount in the source location display a warning
saying 'Not enough products in the source location according
to the quantity ordered.'

This module will extend when will count with decorators
support in version 7.0

    """, 
    "website": "http://vauxoo.com", 
    "license": "", 
    "depends": [
        "stock"
    ], 
    "demo": [], 
    "data": [
        "view/validate_stock_move_product.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}