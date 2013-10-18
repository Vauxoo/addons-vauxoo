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
    "name": "Create employee from users",
    "version": "1.0",
    "author": "Vauxoo",
    "category": "Generic Modules/Human Resources",
    "description": """
Add wizard for create employee from users
===============================================

Module that adds a wizard in res.users model and generated employee from one or many users, only 
and only if there is no other record of employee assigned to the user in question.

    """,
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    'depends': ['hr'],
    "data": [
        "wizard/res_users_view.xml",
    ],
    "demo":[],
    "css": [],
    "test": [],
    "installable": True,
    "active": False,
}
