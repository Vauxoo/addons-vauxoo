# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Juan Funes (juan@vauxoo.com)
#    Audited by: Vauxoo C.A.
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
    "name": "Employee from User",
    "summary": "Create an Employee from the User Form",
    "version": "1.0.1",
    "author": "Vauxoo",
    "category": "Generic Modules/Human Resources",
    "description": """
Add wizard for create employee from users
=========================================

In order to load timesheet correctly is necesary an employee per user.

This wizard enable a technical wizard to create an employee one time the user exists.

The Wizard is added in uses vies model and generate an employee from one or many users,
only if there is no other record of employee assigned to the user in question.
""", 
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "hr"
    ],
    "demo": [],
    "data": [
        "wizard/res_users_view.xml"
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "active": False,
}
