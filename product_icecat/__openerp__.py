# -*- encoding: utf-8 -*-
############################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 Zikzakmedia S.L. (<http://www.zikzakmedia.com>). All Rights Reserved
#    $Id$
#
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
############################################################################################
{
    "name": "Product Information Import from icecat", 
    "version": "1.0", 
    "author": "Zikzakmedia SL", 
    "category": "Added functionality", 
    "description": """
    Import information XML from icecat to OpenERP products.
    This wizard download XML in openerp-server (addons/product_icecat/xml) and after process data mapping line to product import.
    - Language import: User preference or force into wizard (option)
    - HTML Category option: create list details
    - FTP image
    http://www.icecat.biz/
    """, 
    "website": "http://www.zikzakmedia.com", 
    "license": "", 
    "depends": [
        "base", 
        "product_manufacturer", 
        "product_images_olbs"
    ], 
    "demo": [], 
    "data": [
        "security/ir.model.access.csv", 
        "product_icecat.xml", 
        "product_manufacturer.xml", 
        "wizard/wizard_product_icecat.xml"
    ], 
    "test": [
        ""
    ], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: