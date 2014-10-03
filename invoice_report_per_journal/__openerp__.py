# -*- encoding: utf-8 -*- #
############################################################################
#    Module Writen to OpenERP, Open Source Management Solution             #
#    Copyright (C) Vauxoo (<http://vauxoo.com>).                           #
#    All Rights Reserved                                                   #
###############Credits######################################################
#    Coded by: Sabrina Romero (sabrina@vauxoo.com)                         #
#    Planified by: Nhomar Hernandez (nhomar@vauxoo.com)                    #
#    Finance by: COMPANY NAME <EMAIL-COMPANY>                              #
#    Audited by: author NAME LASTNAME <email@vauxoo.com>                   #
############################################################################
#    This program is free software: you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation, either version 3 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>. #
############################################################################
{
    "name": "Account Invoice Per Journal Report", 
    "version": "1.0", 
    "author": "Vauxoo", 
    "category": "Generic Modules", 
    "description": """
Adds a "Report" field on the journal model and a "Print Invoice" button on the
customer invoices view which calls a wizard to print an invoice on a report per
journal enviroment.

This module allows the generation of txt reports using the following
convention:

* Must be a report wizard type to return the txt report.
* The report wizard type must have the same name as his counterpart in pdf
format concatenating the following string ' txt' in the report name.

In this way the module generates both reports, making available for download
the report txt.
    """, 
    "website": "http://www.vauxoo.com/", 
    "license": "AGPL-3", 
    "depends": [
        "account", 
        "report_webkit"
    ], 
    "demo": [], 
    "data": [
        "data/data.xml", 
        "view/account_journal_view.xml", 
        "wizard/invoice_report_per_journal.xml", 
        "view/account_invoice_view.xml", 
        "report/invoice_report_demo.xml"
    ], 
    "test": [
        "test/invoice_report_per_journal.yml"
    ], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: