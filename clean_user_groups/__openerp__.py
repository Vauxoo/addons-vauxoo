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
    "name": "Clean Groups", 
    "version": "1.1", 
    "author": "Vauxoo", 
    "category": "Technical", 
    "description": """
Clean Users Groups
====================================
How to
--------------------------------------------
- Select the users to which you want to remove the permissions
- Open de Clean Groups wizard in client windows from users view
- Select both confirm checkbox
- Press Clean Groups

You need have Technical group
""", 
    "website": "http://www.vauxoo.com", 
    "license": "", 
    "depends": [
        "base"
    ], 
    "demo": [], 
    "data": [
        "wizard/clean_group_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: