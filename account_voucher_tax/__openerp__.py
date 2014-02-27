# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: el_rodo_1 (rodo@vauxoo.com)
############################################################################
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
##############################################################################

{
    "name" : "account_voucher_tax",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "description" : """

The tax actually paid/cashed in the move of payment,
====================================================

Creditable VAT.

It is the charge to all your payments i.e: 

Bought a desktop that charge VAT on this desk is the creditable taxes

Retained VAT is retained by suppliers

- The rule is that only a natural person can hold a moral person.

- The exception to this rule is for freight and rental.

Caused VAT is that actually charged to customers.

- When you make a cash sale that VAT is caused

- When you make a sale on credit is transferred iva but when you pay that sale becomes caused VAT

    """,
    "website" : "http://www.vauxoo.com/",
    "license" : "AGPL-3",
    "depends" : [
        "account",
        "account_voucher",
        "account_invoice_tax",
        "analytic",
        "account_move_line_base_tax",
        ],
    "demo" : [
    "demo/account_voucher_tax_demo.xml", ],
    "data" : [
        "account_tax_view.xml",
        "account_voucher_tax_view.xml",
        "security/ir.model.access.csv",
        ],
    "test": [
        'test/account_voucher_taxes.yml',
        'test/account_voucher_tax_round_off.yml',
        'test/account_voucher_tax_write_off.yml',
        'test/account_voucher_tax_currency_diff.yml',
    ],
    "installable" : True,
    "active" : False,
}
