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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
{
    "name": "Overwrite field standard_price", 
    "version": "1.0", 
    "author": "Vauxoo", 
    "category": "Security", 
    "description": """
Fixed groups on field standard_price
====================================

This module is created because in the definiton of field **standard_price* on the module product.product,
the asignation of groups is made in file product.py in model definition:

'standard_price': fields.float('Cost', digits_compute=dp.get_precision('Product Price'), help="Cost price of the product used for standard stock valuation in accounting and used as a base price on purchase orders.", groups="base.group_user"),

This way forces to allows work with the groups **base.group_user**.

    """, 
    "website": "http://www.vauxoo.com", 
    "license": "", 
    "depends": [
        "base", 
        "product"
    ], 
    "demo": [], 
    "data": [], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}