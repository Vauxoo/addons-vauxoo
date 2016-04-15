# coding: utf-8
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
{
    "name": "Product Image Gallery",
    "version": "9.0.0.0.6",
    "author": "Sharoon Thomas, Open Labs Business Solutions",  # pylint: disable=C8101
    "category": "Added functionality - Product Extension",
    "website": "http://openlabs.co.in/",
    "license": "GPL-3",  # pylint: disable=C8102
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
}
