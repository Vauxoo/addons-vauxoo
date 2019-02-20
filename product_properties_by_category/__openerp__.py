# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
###############################################################################
#    Credits:
#    Coded by: Hugo Adan <hugo@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

{
    "name": "Product Properties by Category",
    "summary": "Set Product Default Properties from the Product Category",
    "version": "10.0.0.1.6",
    "author": "Vauxoo",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "category": "Product",
    "depends": [
        "purchase_requisition",
    ],
    "data": [
        "view/product_category.xml",
    ],
    "demo": [],
    "test": [],
    "qweb": [],
    "js": [],
    "css": [],
    "installable": True,
}
