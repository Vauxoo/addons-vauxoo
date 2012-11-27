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
        
        new_orders = {}
        mrp_production_pool = self.pool.get('mrp.production')
        old_orders = []
        
        for procurement in self.browse(cr, uid, ids):
            if (procurement.state == 'draft') and (procurement.product_id.supply_method=='produce'):
                print procurement.product_id.name, "nombre de productos en draft y a producir"
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
                        'product_qty' : self.pool.get('product.uom')._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, to_uom_id=procurement.product_id.uom_id.id),
                        'product_uom' : procurement.product_id.uom_id.id,
                        'procure_method' : procurement.procure_method
                    })
                else:
                    if procurement.name:
                        order_infos['name'] = (order_infos['name'] or '') + ',' + procurement.name
                    if procurement.origin:
                        order_infos['origin'] = (order_infos['origin'] or '') + ',' + procurement.origin
                    if procurement.product_qty:
                        order_infos['product_qty'] = (order_infos['product_qty'] or 0) + self.pool.get('product.uom')._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, to_uom_id=procurement.product_id.uom_id.id)
                if procurement.production_id.id not in old_orders:
                    old_orders.append(procurement.production_id.id)
            
        allorders = []
        allproductions = []
        orders_info = {}
        for order_key, (order_data, old_ids) in new_orders.iteritems():
        # skip merges with only one order
            if len(old_ids) < 2:
                allorders += (old_ids or [])
                continue

            # create the new procurement order
            neworder_id = self.create(cr, uid, order_data)
            orders_info.update({neworder_id: old_ids})
            allorders.append(neworder_id)
            for old_id in old_ids:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'procurement.order', old_id, 'button_cancel', cr)
            wf_service.trg_validate(uid, 'procurement.order', neworder_id, 'button_confirm', cr) #TODO: to validate when no bom
            new_production_id = self.pool.get('procurement.order').action_produce_assign_product(cr, uid, [neworder_id], context=context)
            if old_orders[0]:
                print old_orders, "sdf"
                mrp_production_pool.write(cr, uid, old_orders, {'subproduction_ids': [(4, new_production_id)]})
            allproductions.append(new_production_id)

        return allproductions #or True
procurement_order()