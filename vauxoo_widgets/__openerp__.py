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
    "name": "Vauxoo Widgets", 
    "version": "0.1", 
    "author": "Vauxoo", 
    "category": "Tools", 
    "description": """
Widgets to customize the openerp views with Qweb extension
===========================================================
If you need add a custom widget in your module you must create it in this
module and make depend your module of this


    """, 
    "website": "http://www.vauxoo.com", 
    "license": "", 
    "depends": [
        "portal_home"
    ], 
    "demo": [], 
    "data": [], 
    "test": [], 
    "js": [
        "static/src/js/vauxoo_widgets.js"
    ], 
    "css": [
        "static/src/css/vauxoo_widget.css"
    ], 
    "qweb": [
        "static/src/xml/vauxoo_widget.xml"
    ], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}