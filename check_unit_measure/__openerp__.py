# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    "name": "Unit Measure Check", 
    "version": "1", 
    "author": "Vauxoo", 
    "category": "Sale, Purchase and Warehousee", 
    "description": """

Unit Measure Check
====================================
This module was created to check the units measured in all operations where we use a product,
for always set the unit measure that this product has and confirm quantity for operation line

Improvements

Inherit Sale, Purchase, Stock and Account to add constraint to avoid sale order validate with diferent 
unit measure indicated on the product or diferent quantity compute on the unit measure.

""", 
    "website": "http://www.vauxoo.com", 
    "license": "", 
    "depends": [
        "sale", 
        "purchase", 
        "product", 
        "stock", 
        "account"
    ], 
    "demo": [], 
    "data": [
        "wizard/stock_return_picking_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: