# coding: utf-8
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
    "name": "MRP variation webkit report",
    "version": "8.0.0.1.6",
    "author": "Vauxoo",
    "category": "Reporting",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "mrp",
        "report_webkit",
        "mrp_variation",
        "mrp_subproduction",
        "mrp_subproduct_pt_planified"
    ],
    "demo": [],
    "data": [
        "data.xml",
        "mrp_webkit_report.xml",
        "wizard/wizard_report_variation.xml"
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": False,
    "auto_install": False,
}
