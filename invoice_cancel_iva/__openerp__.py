#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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
    "name" : "Invoice Cancel with withholding vat",
    "version" : "0.1",
    "depends" : ['account','account_move_cancel','l10n_ve_withholding_iva'],
    "author" : "Vauxoo",
    "description" : """
    Cancels invoices with vat withholding, will be passed to draft and calls 
    mediande vailadadas workflow automatically, keeping the same document that 
    generated initially wittholding
    """,
    "website" : "http://vauxoo.com",
    "category" : "Generic Modules",
    "init_xml" : [],
    "demo_xml" : [],
    "test": [ ],
    "update_xml" : [
    'workflow/account_workflow.xml', 
    
    
    
    ],
    "active": False,
    "installable": True,
}
