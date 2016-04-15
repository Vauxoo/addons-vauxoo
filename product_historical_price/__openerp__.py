# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###########################################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
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
##############################################################################
#                    "security/groups.xml",
{
    "name": "Product Historical Price",
    "version": "9.0.0.0.6",
    "author": "Vauxoo",
    "category": "Generic Modules/Product",
    "website": "http://Vauxoo.com",
    "license": "",
    "depends": [
        "product",
        "decimal_precision",
        "account",
        "sale",
        "base_action_rule",
    ],
    "demo": [],
    "data": [
        "view/product_view.xml",
        "data/product_data.xml",
        "data/action_server_data.xml",
        "security/ir.model.access.csv"
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
}
