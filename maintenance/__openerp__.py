# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Julio Serna(julio@vauxoo.com)
############################################################################
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
    "name" : "Maintenance",
    "version" : "1.0",
    "author" : "Tecnos",
    "category" : "Generic Modules/Maintenance",
    "website" : "",
    "description": """
        Modulo de Mantenimientos para tractos
    """,
    "depends" : ["product","base","stock"],
    "init_xml" : [],
    "data_xml" : [],
    "demo_xml" : [
        "demo/maintenance_demo.xml"
    ],
    "update_xml" : [
        "maintenance_wizard.xml",
        "maintenance_view.xml",
        "maintenance_report.xml"],
    "active": False,
    "installable": True
   }
