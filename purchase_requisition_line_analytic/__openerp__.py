# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
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
    "name": "Purchase Requisition Line Analytic", 
    "version": "1.0", 
    "author": "Vauxoo", 
    "category": "", 
    "description": """
A account analytic is added in purchase requisition lines

Add analytic account on purchase requisition line, so the purchase order takes
the account analytic value from the purchase requisition.
""", 
    "website": "http://www.vauxoo.com/", 
    "license": "", 
    "depends": [
        "account_analytic_plans", 
        "purchase_requisition", 
        "purchase_requisition_line_view", 
        "pr_line_related_po_line"
    ], 
    "demo": [], 
    "data": [
        "view/purchase_requisition_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}