# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Nhomar <nhomar@vauxoo.com>
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
    "name" : "Account Budget Improvements",
    "version" : "1.0",
    "author" : "Vauxoo",
    'category' : 'Accounting & Finance',
    "description" : """
Improvements to Account Budget
==============================

- Added concept of "Estimated Forecast", It is an amount which represent the
  estimated amount per budget line that the person who report the budget line
  estimate comply in some moment.

- Added concept of "Actual Amount": The actual amount is the amount related to
  the sum of account in the fiscal position, with or without
  account_analityc_line this amount will be recorded in db and will change only
  with the change on the workflow.

- Added the concept of "Printed Budget" using the original workflow available
  on the budget we must include the concept of:

  - Posted Date: When the accountant Manager dictaminate that the amount is
    ready to be reviewed for the Local CFO.

  - Approved Date: When the local CFO says that the Budget can be sent to the
    CEO.

  - Received Date: When the CEO says that the budget is received.

The Account Budget view will be used to comply with need to show the executed
Budget per period.
    """,
    "website" : "http://www.vauxoo.com/",
    "license" : "AGPL-3",
    "depends" : [
        "account_budget",
        "account_accountant",
        "ifrs_report",
        "web_kanban",
    ],
    "data" : [
        "view/account_budget_view.xml",
        "security/res_groups.xml",
    ],
    "demo" : [
    ],
    "css": [
        "static/src/css/account_budget.css",
    ],
    "js": [
        "static/src/js/account_budget_imp.js",
    ],
    "test" : [
    ],
    "installable" : True,
    "active" : False,
}
