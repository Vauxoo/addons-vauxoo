#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral          <kathy@vauxoo.com>
#    Planified by: Humberto Arocha       <hbto@vauxoo.com>
#    Audited by: Humberto Arocha         <hbto@vauxoo.com>
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
    "name": "Expenses Replenishment Tax",
    "version": "0.1",
    "depends": [
        "account_invoice_tax",
        "hr_expense_replenishment",
        "account_voucher_tax"
        ],
    "author": "Vauxoo",
    "description": """
Create Entries Tax Effectively Paid :
=====================================

This module creates the tax effectively paid of the invoices associated
with the expense
""",
    "website": "http://openerp.com.ve",
    "category": "HR Module",
    "init_xml": [],
    "demo_xml": [],
    "update_xml": [
        'view/hr_expense_view.xml', 
    ],
    "active": False,
    "installable": True,
}
