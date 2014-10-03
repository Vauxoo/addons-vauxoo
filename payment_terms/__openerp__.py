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
    "name": "Payments Term", 
    "version": "0.1", 
    "author": "Vauxoo", 
    "category": "Generic Modules", 
    "description": """
    Add Payments terms by partner, Each payments termn is set in each partner
    and each partner have a different payment termn by company,

    These fields are located in the Accounting tab, above Others terms added by
    accounting module.

    The Payment term is in sale, stock,purchase and invoice modules and is send 
    through are models
                    """, 
    "website": "http://www.vauxoo.com", 
    "license": "", 
    "depends": [
        "base", 
        "stock", 
        "sale", 
        "purchase", 
        "account"
    ], 
    "demo": [], 
    "data": [
        "view/account_view.xml", 
        "view/partner_view.xml", 
        "view/purchase_view.xml", 
        "view/sale_view.xml", 
        "view/stock_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: