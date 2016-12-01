# coding: utf-8
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
    "name": "Expenses Replenishment",
    "version": "8.0.0.0.6",
    "author": "Vauxoo",
    "category": "HR Module",
    "website": "http://openerp.com.ve",
    "license": "",
    "depends": [
        "hr_expense",
        "account_invoice_line_currency",
        "hr_expense_analytic",
        "account_move_report"
    ],
    "demo": [],
    "data": [
        "security/hr_security.xml",
        "wizard/hr_expense_wizard_view.xml",
        "view/account_invoice_view.xml",
        "view/hr_expense_view.xml",
        "workflow/workflow.xml"
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": False,
    "auto_install": False,
}
