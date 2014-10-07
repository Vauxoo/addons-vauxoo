# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
{
    "name": "Purchase order lines with discounts", 
    "version": "1.0", 
    "author": "Tiny, Acysos S.L.", 
    "category": "Generic Modules/Sales & Purchases", 
    "description": """
    It allows to define a discount per line in the purchase orders. This
    discount can be also negative, interpreting it as an increment.
    """, 
    "website": "", 
    "license": "", 
    "depends": [
        "stock", 
        "purchase"
    ], 
    "demo": [], 
    "data": [
        "purchase_discount_view.xml", 
        "report/purchase_discount_report.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}