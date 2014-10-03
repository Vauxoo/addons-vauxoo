# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: nhomar@vauxoo.com,
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@vauxoo.com
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
##############################################################################
{
    "name": "Split Invoice Button", 
    "version": "0.1", 
    "author": "Vauxoo", 
    "category": "Localization", 
    "description": """
For legal reasons in Venezuela we need just ONE invoice per page, with this module depending on your company configuration you will stablish the number of lines per invoice, with this you will be able of:

 1.-Add module for establishing the number of lines per invoice
 2.-Split Invoice according number of lines per invoice once you confirm it.

-------Testing Instructions--------
Once you installed the module:

1.- Go to Administration - Companies, open one of your companies (if more than one) and
    open the Configuration page.
2.- Set a number of lines per invoice on the corresponding field.

3.- Go to Account - Clients - Client Invoices and create a new invoice with more lines
    than you previously specified on the company configuration

4.- Validate the invoice document

5.- Click Search Asociated button

The document should be now splited on N invoices with the number of lines that you specified

This button allows the user view all generated invoices

 """, 
    "website": "http://vauxoo.com", 
    "license": "", 
    "depends": [
        "account"
    ], 
    "demo": [], 
    "data": [
        "view/invoice_view.xml", 
        "security/split_invoice_security.xml", 
        "security/ir.model.access.csv"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}