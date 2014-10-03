#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Rafael Silva <rsilvam@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
{
    "name": "IFRS", 
    "version": "0.2", 
    "author": "Vauxoo", 
    "category": "Generic Modules", 
    "description": """ International Financial Reporting Standards Module 
Instructions:
=============
How to print the report in PDF or spreadsheet in the following video: http://www.youtube.com/watch?v=zcxS9zO04FQ""", 
    "website": "http://www.vauxoo.com", 
    "license": "", 
    "depends": [
        "base", 
        "account_periods_initial", 
        "account", 
        "report_webkit"
    ], 
    "demo": [], 
    "data": [
        "security/security.xml", 
        "security/ir.model.access.csv", 
        "data/data.xml", 
        "data/data1.xml", 
        "view/ifrs_view.xml", 
        "report/report_ifrs.xml", 
        "wizard/ifrs_report_wizard_view.xml", 
        "data/data_ifrs.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: