# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://www.vauxoo.com>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Humberto Arocha <humbertoarocha@gmail.com>
#    Audited by: Humberto Arocha <humbertoarocha@gmail.com>
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
    "name": "MRP WorkOrder Variation", 
    "version": "1.0", 
    "author": "Vauxoo C.A", 
    "category": "MRP", 
    "description": """

MRP WorkOrder Variation
=======================

Lets have a detailed control of the number of products in and out in a work order. That is,
this module adds a table in the work orders with the real products that are received and outgoing.
In this way the user can make a comparison of the variation of quantities and avoid loss of
material.

""", 
    "website": "http://vauxoo.com", 
    "license": "AGPL-3", 
    "depends": [
        "mrp", 
        "mrp_operations"
    ], 
    "demo": [], 
    "data": [
        "view/mrp_production_workcenter_line_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}