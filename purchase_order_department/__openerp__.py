#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
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
    "name": "Purchase Order Department", 
    "version": "1.0", 
    "author": "Vauxoo", 
    "category": "purchase", 
    "description": """
Purchase Order Department
=========================

Add a department field to the purchase order model. This check the purchase
order requisitor (user) and fill the department field with the requisitor
employee info. Also add a search filter by text to search the department name
and a gruop by filter by department.

Note: this module do not work propertly for users with multiple employees.
""", 
    "website": "http://www.vauxoo.com/", 
    "license": "", 
    "depends": [
        "purchase", 
        "hr", 
        "purchase_order_requisitor", 
        "purchase_requisition_department"
    ], 
    "demo": [], 
    "data": [
        "view/purchase_order_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}