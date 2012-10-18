# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: fernandoL (fernando_ld@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import pooler
import wizard
import netsvc
from tools.translate import _
import tools
import os
from osv import osv, fields
import time
from tools import ustr

class mrp_production(osv.osv):
    _inherit = "mrp.production"
    
    """
    """
    def create_production_wizard(self, cr, uid, product, list_produce, context):
        """ creates the production order
        @param product id to create
        @return: True
        """
        print product.id,"ids"
        print list_produce," list produce"
        #crear datos de orden de produccion y luego crear hijines
        production_order_dict = {
            'name' : self.pool.get('ir.sequence').get(cr, uid, 'mrp.production'),
            'date_planed' : lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
            'product_id' : product.id,
            'product_qty' : 1,
            'product_uom' : product.uom_id.id,
            'location_src_id': 12,
            'location_dest_id': 12,
            'state' : 'draft'
        }
        print production_order_dict
        new_id = self.create(cr, uid, production_order_dict)
        print new_id, " = new id"
        for line in list_produce:
            production_scheduled_dict = {
                'name': line['name'],
                'product_id': line['product_id'],
                'product_qty': line['product_qty'],
                'product_uom': line['product_uom'],
                'production_id': new_id,
            }
            self.pool.get('mrp.production.product.line').create(cr, uid, production_scheduled_dict)
        
        mrp_pt_planifed_dict = {
            'product_id' : product.id,
            'quantity' : 1,
            'production_id' : new_id,
            'product_uom' : product.uom_id.id,
        }
        self.pool.get('mrp.pt.planified').create(cr, uid, mrp_pt_planifed_dict)
        return True
    
mrp_production()