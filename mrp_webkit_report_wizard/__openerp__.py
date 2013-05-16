# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: fernandoL (fernando_ld@vauxoo.com)
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
    "name" : "MRP variation webkit report",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Reporting",
    "description" : """This module adds a report of the variation on production orders of the selected product
    in the selected range of time""",
    "website" : "http://www.vauxoo.com/",
    "license" : "AGPL-3",
    "depends" : ["mrp", "report_webkit", "mrp_variation", "mrp_subproduction", "mrp_subproduct_pt_planified"],
    "data": [],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["data.xml",
        "mrp_webkit_report.xml",
        "wizard/wizard_report_variation.xml"],
    "installable" : False,
    "active" : False,
}
