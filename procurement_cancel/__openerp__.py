# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: echeverrifm (echeverrifm@vauxoo.com)
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
    "name": "Procurement Cancel",
    "version": "1.1",
    "author": "Vauxoo",
    "category": "",
    "description": """
Allow cancel massively Procurements.

When it is necesary:

When you configure stock rules and trigger the schedulers sometimes
you maybe will not be agreed with some of the procurements it will
allow you cancel them by groups one time you make filters.
    """,
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "base",
        "procurement",
    ],
    "demo": [],
    "data": [
        "security/procurement_cancel.xml",
        "wizard/procurement_cancel_view.xml",
    ],
    "installable": True,
    "active": False,
}
