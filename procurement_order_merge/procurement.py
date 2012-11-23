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
from osv.orm import browse_record, browse_null

class procurement_order(osv.osv):
    _inherit='procurement.order'
    
    def do_merge(self, cr, uid, ids, context={}):
        
        def make_key(br, fields):
            list_key = []
            for field in fields:
                field_val = getattr(br, field)
                if field in ('product_id', 'location_id', 'procure_method'):
                    if not field_val:
                        field_val = False
                if isinstance(field_val, browse_record):
                    field_val = field_val.id
                elif isinstance(field_val, browse_null):
                    field_val = False
                elif isinstance(field_val, list):
                    field_val = ((6, 0, tuple([v.id for v in field_val])),)
                list_key.append((field, field_val))
            list_key.sort()
            return tuple(list_key)
        
        procurement_order = self.pool.get('procurement.order')
        
        res_product = {}
        res_location = {}
        res_method = {}
        res_products = {}
        res_name = {}
        res_origin = {}
        product_uom = {}
        proc_ids_to_cancel = {}
        new_orders = {}
        ok = False
        
        for procurement in self.browse(cr, uid, ids):
            order_key = make_key(procurement, ('product_id', 'location_id', 'procure_method'))
            new_order = new_orders.setdefault(order_key, ({}, []))
            new_order[1].append(procurement.id)
            order_infos = new_order[0]
            if not order_infos:
                order_infos.update({
                    'name' : procurement.name,
                    'origin' : procurement.origin,
                    'product_id' : procurement.product_id.id,
                    'location_id' : procurement.location_id.id,
                    'product_qty' : procurement.product_qty,
                    'product_uom' : procurement.product_uom.id,
                    'procure_method' : procurement.procure_method
                })
            else:
                #if procurement.date_order < order_infos['date_order']:
                #    order_infos['date_order'] = procurement.date_order
                #if procurement.notes:
                #    order_infos['notes'] = (order_infos['notes'] or '') + ('\n%s' % (porder.notes,))
                if procurement.name:
                    order_infos['name'] = (order_infos['name'] or '') + ',' + procurement.name
                if procurement.origin:
                    order_infos['origin'] = (order_infos['origin'] or '') + ',' + procurement.origin
                if procurement.product_qty:
                    order_infos['product_qty'] = (order_infos['product_qty'] or 0) + self.pool.get('product.uom')._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, to_uom_id=procurement.product_id.uom_id.id)
                    ###########
            print new_order,"<- new_order final de for\n"
            
            
            #########
        allorders = []
        orders_info = {}
        for order_key, (order_data, old_ids) in new_orders.iteritems():
        # skip merges with only one order
            print order_key, "<- order key"#
            print order_data, old_ids, "<- order data y old ids\n"#
            if len(old_ids) < 2:
                allorders += (old_ids or [])
                continue

            # cleanup order line data
            #for key, value in order_data['order_line'].iteritems():
            #    del value['uom_factor']
            #    value.update(dict(key))
            #order_data['order_line'] = [(0, 0, value) for value in order_data['order_line'].itervalues()]

            # create the new order
            neworder_id = self.create(cr, uid, order_data)
            orders_info.update({neworder_id: old_ids})
            allorders.append(neworder_id)

            # make triggers pointing to the old orders point to the new order
            for old_id in old_ids:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'procurement.order', old_id, 'button_cancel', cr)
                #wf_service.trg_redirect(uid, 'purchase.order', old_id, neworder_id, cr)
                #wf_service.trg_validate(uid, 'purchase.order', old_id, 'purchase_cancel', cr)
            
            ###########
            """
            if procurement.state <> 'draft':
                ok = True
                 
            res_product.setdefault(procurement.product_id.id, 0)
            res_product[procurement.product_id.id] += 1
            res_products.setdefault(procurement.product_id.id, 0)
            res_products[procurement.product_id.id] += self.pool.get('product.uom')._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, to_uom_id=procurement.product_id.uom_id.id)
            res_location.setdefault(procurement.product_id.id, procurement.location_id.id)
            res_method.setdefault(procurement.product_id.id, procurement.procure_method)
            res_name.setdefault(procurement.product_id.id, [])
            res_name[procurement.product_id.id].append(procurement.name)
            res_origin.setdefault(procurement.product_id.id, [])
            res_origin[procurement.product_id.id].append(procurement.origin)
            product_uom.setdefault(procurement.product_id.id, procurement.product_id.uom_id.id)
            proc_ids_to_cancel.setdefault(procurement.product_id.id, [])
            proc_ids_to_cancel[procurement.product_id.id].append(procurement.id)
            
        if ok == True:
            raise osv.except_osv(_('Error'), _('Procurements must be in state draft') )
            
        for lin in res_products:
            if res_product[lin] > 1:
                print lin,'impirmo lins'
                print proc_ids_to_cancel, "<- proc_ids_to_cancel"
                print res_origin, "<- res_origin"
                procure_name = ','.join( map(str, res_name[lin]) )
                procure_origin = ','.join( map(str, res_origin[lin]) )
                procurement_order.create(cr, uid, {
                    'name' : procure_name,
                    'origin' : procure_origin,
                    'product_id' : lin,
                    'location_id' : res_location[lin],
                    'product_qty' : res_products[lin],
                    'product_uom' : product_uom[lin],
                    'procure_method' : res_method[lin]
                })
                for proc in proc_ids_to_cancel[lin]:
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'procurement.order', proc, 'button_cancel', cr)
    """
        return True
procurement_order()