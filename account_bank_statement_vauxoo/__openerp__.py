# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Coded and Planified by Nhomar Hernandez <nhomar@vauxoo.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Fixes and Imrpovements to Bank Statement management",
    "version": "9.0.0.0.6",
    "author": "Vauxoo",
    "category": "Accounting & Finance",
    "website": "http://vauxoo.com",
    "license": "",
    "depends": [
        "account"
    ],
    "demo": [],
    "data": [
        "security/bank_statement_security.xml",
        "security/ir.model.access.csv",
        "view/account_bank_statement_view.xml",
        "view/account_invoice_view.xml",
        "view/account_journal_view.xml",
        "data/data.xml"
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "external_dependencies": {
        "python": ["xlrd"],
    },
}
