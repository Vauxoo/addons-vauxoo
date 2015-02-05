# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# ##############Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################
{
    "name": "Issue Management enhancement.",
    "version": "0.1",
    "author": "Vauxoo",
    "category": "Generic Modules",
    "description": """
Improvements that this module does.
===================================

- Add the possibility to make consistent task - issue and contact, adding a
button that propose set the same analytic account for the 3 of them.

- Add a button to add the function "Take for me." it allows with a simple click
assign to the user connected the issue.

TODO:
-----

This module will have all features specific to solve little issues in the
project_issue module.
    """,
    "website": "http://vauxoo.com",
    "depends": [
        "project",
        "project_issue",
    ],
    "demo": [],
    "data": [
        "view/project_issue_view.xml",
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "active": False
}
