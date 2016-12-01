# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>+
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
    "name": "Unit of Measure Security",
    'summary': "Split Unit of measure usability for Sales/Purchases/Warehouse",
    "version": "8.0.0.1.6",
    "author": "Vauxoo",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "category": "Security",
    "depends": [
        "account",
        "mrp",
        "purchase_requisition",
        "sale",
        "hr_expense",
    ],
    "data": [
        "security/uom_groups.xml",
        "view/account_view.xml",
        "view/stock_view.xml",
        "view/mrp_view.xml",
        "view/purchase_view.xml",
        "view/sale_view.xml",
        "view/procurement_view.xml",
        "view/product_view.xml",
        "view/hr_expense_view.xml",
    ],
    "demo": [],
    "test": [],
    "qweb": [],
    "js": [],
    "css": [],
    "installable": False,
}
