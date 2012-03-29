# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Javier Duran <javieredm@gmail.com>,
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@vauxoo.com
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

{
    "name" : "salem_uom_group"                                                                              ,
    "version" : "0.1"                                                                                       ,
    "depends" : ["sale"]                                                                                    ,
    "author" : "Openerp Venzuela"                                                                           ,
    "description" : """
    What do this module:
    Add multi product uom sum of order line.
                    """                                                                                     ,
    "website" : "http://vauxoo.com"                                                                     ,
    "category" : "Generic Modules/MRP"                                                                      ,
    "init_xml" : [
    ]                                                                                                       ,
    "demo_xml" : [
    ]                                                                                                       ,
    "update_xml" : [
        "security/groups.xml"                                                                               ,
        "security/ir.model.access.csv"                                                                      ,
        "view/sale_uom_group_view.xml"                                                                      ,

    ]                                                                                                       ,
    "active": False                                                                                         ,
    "installable": True                                                                                     ,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

