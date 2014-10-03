#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
################# Credits######################################################
#    Coded by: Luis Escobar <Luis@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
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
    "name": "Convert Note to Task", 
    "version": "1.0", 
    "author": "Vauxoo", 
    "category": "Tools", 
    "description": """
Convert Note to Task
====================
    Add a button in Notes showing a wizard to convert the note into a task
    asking:
            1. - Estimated time for this task.
            2.- Associate Project.
            3.- Date to end.
            """, 
    "website": "http://vauxoo.com", 
    "license": "", 
    "depends": [
        "base", 
        "note", 
        "project"
    ], 
    "demo": [], 
    "data": [
        "wizard/convert_note_view.xml", 
        "view/note_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: