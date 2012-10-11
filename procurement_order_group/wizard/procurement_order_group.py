# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
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
import time
from osv import osv, fields
import decimal_precision as dp
from tools.translate import _

class procurement_order_group(osv.osv_memory):
    _name='procurement.order.group'
    
    def procurement_group(self, cr, uid, ids, context=None):
        procurement_order = self.pool.get('procurement.order')
        if context is None:
            context = {}
        procurement_ids = context.get('active_ids', [])
        res_product = {}
        res_location = {}
        res_method = {}
        res_name = []
        res_origin = []
        
        for procurement in procurement_order.browse(cr, uid, procurement_ids):
            res_product.setdefault(procurement.product_id.id, 0)
            res_product[procurement.product_id.id] += self.pool.get('product.uom')._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, to_uom_id=procurement.product_id.uom_id.id)
            res_location.setdefault(procurement.location_id.id, 1)
            res_method.setdefault(procurement.procure_method, 1)
            res_name.append(procurement.name)
            res_origin.append(procurement.origin)
            product_uom = procurement.product_id.uom_id.id
        if len(res_product) > 1 or len(res_location) > 1 or len(res_method) > 1:
            print 'imprimo len mayor'
        else:
            procure_name = ','.join( map(str, res_name) )
            procure_origin = ','.join( map(str, res_origin) )
            procurement_order.create(cr, uid, {
                'name' : procure_name,
                'origin' : procure_origin,
                'product_id' : res_product.items()[0][0],
                'location_id' : res_location.keys()[0],
                'product_qty' : res_product.items()[0][1],
                'product_uom' : product_uom,
                'procure_method' : res_method.keys()[0]
            })
        return {}
    
procurement_order_group()


















