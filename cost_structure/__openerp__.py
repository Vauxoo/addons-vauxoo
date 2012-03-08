#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
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
    "name" : "Cost Structure",
    "version" : "0.1",
    "depends" : ["stock",'product','sale','purchase'],
    "author" : "Vauxoo",
    "description" : """
    """,
    "website" : "http://vauxoo.com",
    "category" : "Generic Modules",
    "init_xml" : ['data/data_load.xml'],
    "demo_xml" : [],
    "test": [ ],
    "update_xml" : [
    'security/cost_structure_security.xml',
    'security/ir.model.access.csv',
    'view/cost_structure.xml',
    'view/product_view.xml',
    'view/sale_view.xml',
    
    
    
    
    ],
    "active": False,
    "installable": True,
}
