# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: nhomar@openerp.com.ve,
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
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
    "name": "mrp Advanced", 
    "version": "0.1", 
    "author": "Openerp Venzuela", 
    "category": "Generic Modules/MRP", 
    "description": """
    What do this module:
    Add cost managment feature to manage of production in mrp.bom Object.
    -- Sum all elements on Bill of Material
    -- If the element on bom child has only a Product Id the cost is taken from product.
    -- If the element has bom children elements the process of calc is the same of parent.

    Validate that the Unit to produce is in the same category of Unit for the product Id to avoid inconsistencies around unit conversion.
    
    Add field of type assets in product.template establishing if product is assets
    Add menu Product Assets, Product for Sale
    
    Add field of type assets in mrp.bom establishing if bom is assets
    Add menu Bom Assets, Bom for Sales
                    """, 
    "website": "http://openerp.com.ve", 
    "license": "", 
    "depends": [
        "mrp", 
        "product", 
        "mrp_routing_cost"
    ], 
    "demo": [], 
    "data": [
        "mrp_po_view.xml", 
        "data/decimal_precision_cost_bom.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: