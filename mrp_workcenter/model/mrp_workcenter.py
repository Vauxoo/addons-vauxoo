#!/usr/bin/python                                                                                                                                  
# -*- encoding: utf-8 -*-                                                       
############################################################################### 
#    Module Writen to OpenERP, Open Source Management Solution                  
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).                 
#    All Rights Reserved                                                        
# Credits######################################################                 
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com>
#              Katherine Zaoral <katherine.zaoral@vauxoo.com>            
#    Planified by: Yanina Aular <yanina.aular@vauxoo.com>
#    Audited by: Humberto Arocha <humbertoarocha@gmail.com>
############################################################################### 
#    This program is free software: you can redistribute it and/or modify       
#    it under the terms of the GNU Affero General Public License as published   
#    by the Free Software Foundation, either version 3 of the License, or       
#    (at your option) any later version.                                        
#                                                                               
#    This program is distributed in the hope that it will be useful,            
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              
#    GNU Affero General Public License for more details.                        
#                                                                               
#    You should have received a copy of the GNU Affero General Public License   
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      
###############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

#class mrp_workcenter(osv.Model):
#
#    _inherit = "mrp.workcenter"
#    _order = "sequence"
#    _columns = {
#        "sequence": fields.integer("Sequence")
#    }
#
#    _sql_constraints = [
#        ("sequence_uniq", "unique(sequence)", "The sequence of the workcenter must be unique!")
#    ]

class mrp_production_workcenter_line(osv.Model):

    _inherit = "mrp.production.workcenter.line"
    _columns = {

        'routing_id' : fields.related('production_id', 'routing_id', type='many2one', relation='mrp.routing', string='Routing' ,store=True),
    }

    def _read_group_workcenter_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        
        routing_obj = self.pool.get('mrp.routing')
        workcenter_obj = self.pool.get('mrp.workcenter')

        workcenter_ids = []
        if context.get('active_id', False):
            routing_brw = routing_obj.browse(cr, uid, 
                context.get('active_id', False), context=context)
            
            for work_line in routing_brw.workcenter_lines:
                workcenter_ids.append( work_line.workcenter_id.id )
            workcenter_ids = map(lambda x: x, set(workcenter_ids))
            work_orders_ids = self.search(cr, uid, [("workcenter_id","in",workcenter_ids),("routing_id","=",context.get('active_id', False))], context=context)
        else:
            workcenter_ids = workcenter_obj.search(cr, uid, [], context=context)       
            work_orders_ids = self.search(cr, uid, [("workcenter_id","in",workcenter_ids)], context=context)

        lista_workcenter = workcenter_obj.browse(cr, uid, workcenter_ids, context=context)
       # lista_workcenter.sort(key=lambda x: x.sequence)
       # lista_workcenter.reverse()


        # Lista de tuplas (id, name)
        result = []
        for i in lista_workcenter:
            result.append( (i.id, i.name) )

        #Si se despliega o no
        visible = {}
        for i in workcenter_ids:
            visible[i] = False
        
        return result, visible

    _group_by_full = {
        'workcenter_id': _read_group_workcenter_ids,
    }
                                 
