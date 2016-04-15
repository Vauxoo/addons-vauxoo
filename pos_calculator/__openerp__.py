# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Luis Escobar <luis@vauxoo.com>
#    Audited by:  Humberto Arocha <humbertoarocha@gmail.com>
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
    "name": "Pos Calculator",
    "version": "8.0.0.0.6",
    "author": "Vauxoo",
    "category": "Point Of Sale",
    "website": "http://vauxoo.com",
    "license": "",
    "depends": [
        "base",
        "point_of_sale"
    ],
    "demo": [],
    "data": [],
    "test": [],
    "js": [
        "static/src/js/backbone-super-min.js",
        "static/src/js/widgets.js"
    ],
    "css": [
        "static/src/css/pos_popup.css",
        "static/src/css/pos.css"
    ],
    "qweb": [
        "static/src/xml/pos.xml"
    ],
    "installable": True,
    "auto_install": False,
}
