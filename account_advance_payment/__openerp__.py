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
    "name": "Account Advance Payment", 
    "version": "1.0", 
    "author": "Vauxoo", 
    "category": "Generic Modules", 
    "description": """
Account Advance Payment
=======================

This module you can help with advance payment of custom and suppliers.

This module adds the fields Account Supplier Advance, Account Customer Advance,
Total Customer Advance and Total Supplier Advance in the view form of the partner.

Also adds the field Transaction Type in the view payments of customs and suppliers.

    """, 
    "website": "http://www.vauxoo.com/", 
    "license": "AGPL-3", 
    "depends": [
        "account", 
        "account_voucher"
    ], 
    "demo": [], 
    "data": [
        "view/res_partner_advance_payment_view.xml", 
        "view/account_voucher_advance_payment_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}