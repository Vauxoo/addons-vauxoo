# -*- encoding: utf-8 -*-
############################################################################
#    Module Writen to OpenERP, Open Source Management Solution             #
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).            #
#    All Rights Reserved                                                   #
###############Credits######################################################
#    Coded by: Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>   #
#    Planified by: Nhomar Hernandez                                        #
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve            #
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
    "name" : "Cost Imex",
    "version" : "0.1",
    "depends" : ["base",'purchase'],
    "author" : "Vauxoo",
    "description" : """
    This module will add new functionality to the purchasing module, allowing import tax charged on the purchase process product line.

    Be modified in view of purchase where adding a new tab will be calculated automatically import taxes
    
    Added a new model to all compute of tax base
                    """,
    "website" : "http://www.vauxoo.com",
    "category" : "Generic Modules",
    "init_xml" : ['data/data_load.xml'],
    "demo_xml" : [    ],
    "update_xml" : [
    'security/percent_imex_security.xml',
    'security/ir.model.access.csv',
    'view/purchase_view.xml',
    'view/percen_imex_view.xml',
                    ],
    "active": False,
    "installable": True,
}
