# -*- encoding: utf-8 -*-
############################################################################
#    Module Writen to OpenERP, Open Source Management Solution             #
#    Copyright (C) Vauxoo (<http://vauxoo.com>).            #
#    All Rights Reserved                                                   #
###############Credits######################################################
#    Coded by: author NAME LASTNAME <email@vauxoo.com>                 #
#    Planified by: Nhomar Hernandez                                        #
#    Finance by: COMPANY NAME <EMAIL-COMPANY>                              #
#    Audited by: Humberto Arocha humberto@vauxoo.com                   #
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
    "name": "Account Invoice Multicompany Report", 
    "version": "0.1", 
    "author": "Vauxoo", 
    "category": "Generic Modules", 
    "description": """
        Adds a "Report" field on the Company model and a "Print Invoice" button on the customer invoices view which calls
        a wizard to print an invoice on a MultiCompany enviroment
                    """, 
    "website": "http://www.vauxoo.com", 
    "license": "", 
    "depends": [
        "account", 
        "multireport_base"
    ], 
    "demo": [], 
    "data": [
        "view/invoice_multicompany_report_view.xml", 
        "wizard/account_invoice_multicompany.xml", 
        "view/invoice_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": False, 
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: