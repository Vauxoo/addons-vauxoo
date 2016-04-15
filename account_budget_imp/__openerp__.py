# coding: utf-8
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
    "name": "Account Budget Improvements",
    "version": "9.0.0.1.6",
    "author": "Vauxoo",
    "category": "Accounting & Finance",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "account_budget",
        "account_accountant",
        "ifrs_report",
        "web_kanban"
    ],
    "demo": [],
    "data": [
        "view/account_budget_view.xml",
        "security/res_groups.xml",
        "data/account_budget_data.xml"
    ],
    "test": [],
    "js": [
        "static/src/js/account_budget_imp.js"
    ],
    "css": [
        "static/src/css/account_budget.css"
    ],
    "qweb": [],
    "installable": True,
    "auto_install": False,
}
