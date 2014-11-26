# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
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
    "name": "Account Voucher Draft", 
    "version": "1.0", 
    "author": "Vauxoo", 
    "category": "", 
    "description": """
Account Voucher Draft
=====================

This module modify the button Pay inside the wizard used to pay an HR Expense
(using an account voucher). This change is made to do not immediately change
the HR Expene to done state.

Notes
-----

- the ``Pay`` window is not really a wizard, is just a pop up window to create
  a account voucher related to the current hr expense document.
- the ``hr_expense_replenishment`` module can be found at lp:addons-vauxoo.

""", 
    "website": "http://www.vauxoo.com/", 
    "license": "", 
    "depends": [
        "account_voucher", 
        "hr_expense_replenishment"
    ], 
    "demo": [], 
    "data": [
        "view/hr_expense_expense_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}