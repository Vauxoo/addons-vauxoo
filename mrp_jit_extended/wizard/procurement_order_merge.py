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
from osv import osv, fields
from tools.translate import _

class procurement_order_merge(osv.osv_memory):
    _inherit='procurement.order.merge'
    
    def procurement_merge(self, cr, uid, ids, context=None):
        procurement_order = self.pool.get('procurement.order')
        mrp_production_pool = self.pool.get('mrp.production')
        if context is None:
            context = {}
        production_ids = context.get('active_ids', [])
        procurement_product_list = []
        procurement_product_records = []
        procurement_ids = []
        product_procurement_dict = {}
        for production_id in production_ids:
            production_data = mrp_production_pool.browse(cr, uid, production_id, context=context)
            for line in production_data.procurement_ids:
                #    line.state == 'draft':
                #    print line.id, "id del procurement"
                #    print line.state, "state"
                #    print line.product_id.name, "producto\n"
                if (line.product_id.id not in procurement_product_list and line.state == 'draft'):
                    procurement_product_list.append(line.product_id.id)
                    print "producto diferente agregado"
                if line.state == 'draft':
                    procurement_product_records.append(line)
                    #procurement_ids.append(line.id)
                    #product_procurement_dict.update({line.product_id.id : procurement_ids.append(line.id)})
                    if product_procurement_dict.get(line.product_id.id) == None:
                        product_procurement_dict[line.product_id.id] = []
                    product_procurement_dict[line.product_id.id].append(line.id)
                    print product_procurement_dict, "diccionario de products y procurements"
        print procurement_product_list, "lista de productos ke aparecen"
        
        #procurement_order.do_merge(cr, uid, procurement_ids, context=context)
        return {}
    
procurement_order_merge()