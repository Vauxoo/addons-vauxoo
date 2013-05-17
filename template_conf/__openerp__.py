##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
###############Credits######################################################
#    Coded by: Vauxoo C.A. (Maria Gabriela Quilarque)          
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
##############################################################################
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
##############################################################################

{
    "name" : "Load Templates Automatically",
    "version" : "0.1",
    "depends" : ["base","project","email_template"],
    "author" : ["Vauxoo",],
    "description" : """
    What do this module:
    When you install this module, load the templates automatically.
    This module contains the following template configured and done to use:
    -Email Template to send email by task.
""",
    "website" : "http://vauxoo.com",
    "category" : "Generic Modules",
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
      "data/project_conf.xml"
    ],
    "active": False,
    "images": [],
    "installable": True,
}
