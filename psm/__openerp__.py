# -*- encoding: utf-8 -*-
############################################################################
#    Module Writen to OpenERP, Open Source Management Solution             #
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).            #
#    All Rights Reserved                                                   #
###############Credits######################################################
#    Coded by: author NAME LASTNAME <email@openerp.com.ve>                 #
#    Planified by: Nhomar Hernandez                                        #
#    Finance by: COMPANY NAME <EMAIL-COMPANY>                              #
#    Audited by: Humberto Arocha humberto@openerp.com.ve                   #
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
    "name": "Serial Picking Manager", 
    "version": "1.0", 
    "author": "Vauxoo", 
    "category": "Product Serialization", 
    "description": """

 What do this module:

 Pedigree and Serialization Manager (PSM) is an integrated mass-serialization and pedigree application
 that enables companies to implement and manage mass serialization of products and share serialized product
 data across the supply chain.

 To Do:

 - Create wizard for product data serialization.
 - Hide native OpenERP wizard.
 - Create action Show serial/lot for products.
 - Create report where the serial printed grouped by porducto.

 If you have a multi-company environment you must:

- Login as admin
- Duplicate the sequence 'PSM', for each company you handle
- Change the prefix of the sequence by company for differentiation

        """, 
    "website": "http://www.vauxoo.com", 
    "license": "", 
    "depends": [
        "base", 
        "stock", 
        "sale", 
        "purchase"
    ], 
    "demo": [], 
    "data": [
        "data/psm_sequence.xml", 
        "workflow/stock_workflow.xml", 
        "wizard/pedigree_serialization_manager.xml", 
        "wizard/stock_invoice_onshipping_view.xml", 
        "view/stock_view.xml", 
        "view/product_view.xml", 
        "report/psm_picking_report.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}