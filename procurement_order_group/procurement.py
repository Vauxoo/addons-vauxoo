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
from osv import osv,fields
from tools.translate import _
import netsvc

class procurement_order(osv.osv):
    _inherit='procurement.order'
    
    def do_group(self, cr, uid, ids, context={}):
        procurement_order = self.pool.get('procurement.order')
        
        res_product = {}
        res_location = {}
        res_method = {}
        res_name = []
        res_origin = []
        ok = False
        
        for procurement in procurement_order.browse(cr, uid, ids):
            
            if procurement.state <> 'draft':
                ok = True
                
            res_product.setdefault(procurement.product_id.id, 0)
            res_product[procurement.product_id.id] += self.pool.get('product.uom')._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, to_uom_id=procurement.product_id.uom_id.id)
            res_location.setdefault(procurement.location_id.id, 1)
            res_method.setdefault(procurement.procure_method, 1)
            res_name.append(procurement.name)
            res_origin.append(procurement.origin)
            product_uom = procurement.product_id.uom_id.id
            
        if ok == True:
            raise osv.except_osv(_('Error'), _('Procurements must be in state draft') )

        if len(res_product) > 1 or len(res_location) > 1 or len(res_method) > 1:
            raise osv.except_osv(_('Error'), _('Procurements can not be merged') )
            
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
        for proc in ids:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'procurement.order', proc, 'button_cancel', cr)
    
    
procurement_order()

