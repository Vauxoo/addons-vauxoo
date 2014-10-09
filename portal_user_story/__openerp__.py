# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
###############Credits######################################################
#    Coded by: Vauxoo C.A. "Nhomar Hernández <nhomar@vauxoo.com>"
#    Planified by: Rafael Silva
#    Audited by: Vauxoo C.A.
##############################################################################
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
    "name" : "Portal Acess for User Story",
    "version" : "0.1",
    "depends" : [
                 "base",
                 "user_story",
                 "portal",
                 "portal_project",
                 ],
    "author" : "Vauxoo",
    "description" : """
This Module only offer Portal Access to customers.

    - List User Stories per Project.
    - Allow Mark Acceptability Criteria as "Accepted".
    - See historical communication on User Story.

The only objective is, easily with add Portal Access to Contacts on a Customer
be able to let them accept user stories.
                    """,
    "website" : "http://vauxoo.com",
    "category" : "Generic Modules",
    "demo" : [
        'demo/demo.xml',
    ],
    "data" : [
        "security/ir_rules.xml",
        "security/ir.model.access.csv",
        'view/portal_view.xml',
    ],
    "active": False,
    "images": [],
    "installable": True,
}
