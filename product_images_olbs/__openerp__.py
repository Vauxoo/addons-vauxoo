#########################################################################
# Copyright (C) 2009  Sharoon Thomas, Open Labs Business solutions      #
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
{
    "name": "Product Image Gallery", 
    "version": "0.1 ", 
    "author": "Sharoon Thomas, Open Labs Business Solutions", 
    "category": "Added functionality - Product Extension", 
    "description": """
    This Module implements an Image Gallery for products.
    You can add images against every product.

    This module is generic but built for Magento ERP connector and
    the upcoming e-commerce system for Open ERP by Open Labs
    """, 
    "website": "http://openlabs.co.in/", 
    "license": "", 
    "depends": [
        "base", 
        "product"
    ], 
    "demo": [], 
    "data": [
        "security/ir.model.access.csv", 
        "views/product_images_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}