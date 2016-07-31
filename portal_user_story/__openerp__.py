# coding: utf-8
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
    "name": "Portal Access for User Story",
    "version": "8.0.0.0.6",
    "depends": [
        "base",
        "user_story",
        "portal",
        "portal_project",
    ],
    "author": "Vauxoo",
    "website": "http://vauxoo.com",
    "license": "AGPL-3",
    "category": "Generic Modules",
    "demo": [
        'demo/demo.xml',
    ],
    "data": [
        "security/ir_rules.xml",
        "security/ir.model.access.csv",
        'view/portal_view.xml',
    ],
    "images": [],
    "installable": True,
}
