# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Julio Serna(julio@vauxoo.com)
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
from osv import fields
from osv import osv
import time
import os
import netsvc
import base64

#~ class tire_brand(osv.osv):
    #~ _name = 'tire.brand'
#~ 
    #~ _columns = {
            #~ 'name': fields.char('nombre', size=64)
        #~ }
#~ 
#~ tire_brand()

#~ class tire_size(osv.osv):
    #~ _name = 'tire.size'
#~ 
    #~ _columns = {
            #~ 'name': fields.char('nombre', size=64)
        #~ }
#~ 
#~ tire_size()

class product_template(osv.osv):
    _inherit = 'product.template'

    #~ def _get_current(self, cr, uid, ids, name, arg, context=None):
        #~ query = """SELECT th.id, MAX(th.date) FROM tire_history th WHERE th.tire_id in (%s) GROUP BY th.id"""%(",".join(map(str, ids)))
        #~ cr.execute(query)
        #~ hist_ids = cr.dictfetchall()
        #~ res = {}
        #~ for hist in self.pool.get('tire.history').browse(cr, uid, map(lambda x: x['id'], hist_ids)):
            #~ res[hist.tire_id.id] = "%s - %s - %s Km"%(hist.tracto_id.name, hist.position, hist.distance)
        #~ for id in ids:
            #~ res.setdefault(id, '')
        #~ return res

    def _get_release(self, cr, uid, ids, name, arg, context=None):
        res = {}
        query = """SELECT product_id, id, MAX(date_release) as date FROM maintenance_order_line WHERE product_id in (%s) AND state='in_progress' GROUP BY product_id, id"""%(",".join(map(str, ids)))
        cr.execute(query)
        for release in cr.dictfetchall():
            res[release['product_id']] = release['id']
        for id in ids:
            res.setdefault(id, '')
        return res

    _columns = {
            #Datos necesarios para los mantenimientos automaticos
            'modelo_id': fields.many2one('tracto.modelo', 'Modelo'),
            'distance': fields.float('Kilometraje'),
            'maintenance_ids': fields.one2many('maintenance.order.line', 'product_id', 'Mantenimientos'),
            'maintenance_id': fields.function(_get_release, method=True, string="Mantenimiento", type="many2one", relation="maintenance.order.line"),
            'product_image': fields.binary('Image'),
            'model': fields.char('Modelo', size=16),
            #Datos para las llantas
            #~ 'tire_state': fields.selection([('nueva', 'Nueva'), ('usada', 'Usada'), ('renovada','Renovada'), ('original','Original')],'Estado'),
            #~ 'brand_id': fields.many2one('tire.brand', 'Marca'),
            #~ 'size': fields.many2one('tire.size', 'Medida'),
            #~ 'tire_type': fields.selection([('convencional','Convencional'),('direccional','Direccional'),('radial','Radial'),('traccion','Traccion')], 'Tipo de Piso'),
            #~ 'renew': fields.integer('Renovado'),
            #~ 'talacha': fields.integer('Talachas'),
            #~ 'recorrido': fields.integer('Recorrido'),
            #~ 'capas': fields.integer('Numero de Capas'),
            #~ 'profundidad': fields.float('Profundidad'),
            #~ 'date_tire': fields.date('Fecha Revision'),
            #Posicionamiento en ejes
            #EJE 1
            #~ 'front_left': fields.many2one('product.product', 'Frente Izquierdo', readonly=True),
            #~ 'front_right': fields.many2one('product.product', 'Frente Derecho', readonly=True),
            #EJE 2
            #~ 'rear_left': fields.many2one('product.product', 'Izquierdo', readonly=True),
            #~ 'rear_left2': fields.many2one('product.product', 'Izquierdo 2', readonly=True),
            #~ 'rear_right': fields.many2one('product.product', 'Derecho', readonly=True),
            #~ 'rear_right2': fields.many2one('product.product', 'Derecho 2', readonly=True),
            #EJE 3
            #~ 'rear2_left': fields.many2one('product.product', 'Izquierdo', readonly=True),
            #~ 'rear2_left2': fields.many2one('product.product', 'Izquierdo 2', readonly=True),
            #~ 'rear2_right': fields.many2one('product.product', 'Derecho', readonly=True),
            #~ 'rear2_right2': fields.many2one('product.product', 'Derecho 2', readonly=True),
            #Refacciones . . . duh!!!
            #~ 'refaccion1': fields.many2one('product.product', 'Refaccion 1', readonly=True),
            #~ 'refaccion2': fields.many2one('product.product', 'Refaccion 2', readonly=True),
            #~ 'axle_type': fields.selection([('',''),
                    #~ ('tracto6','Tracto 6 Llantas'),
                    #~ ('tracto10','Tracto 10 Llantas'),
                    #~ ('caja4','Caja 4 Llantas'),
                    #~ ('caja8','Caja 8 Llantas')],'Type'),
#~ 
            #~ 'history_ids': fields.one2many('tire.history', 'tire_id', 'Historial'),
            #~ 'current_pos': fields.function(_get_current, method=True, string="Posicion Actual",type="char", size="64"),
            
        }

product_template()

#~ class product_product(osv.osv):
    #~ _inherit = 'product.product'
#~ 
    #~ def _search_routing_available(self, cr, uid, obj, name, args, context={}):
        #~ ids = []
        #~ for product in self.browse(cr, uid, self.search(cr, uid, [('id','<>',0)], context=context), context=context):
            #~ if args[0][2] and product.routing_available:
                #~ ids.append( product.id )
            #~ elif not args[0][2] and not product.routing_available:
                #~ ids.append( product.id )
        #~ #if not ids: return [('id', '=', 0)]
        #~ return [('id', 'in', ids)]
#~ 
    #~ def _get_routing_available(self, cr, uid, ids, field_name, args, context={}):
        #~ res = {}
        #~ for product in self.browse(cr, uid, ids, context=context):
            #~ available = False
            #~ if (not product.routing_state or product.routing_state in ('draft', 'done', 'cancel')) and not product.maintenance_id:
                #~ available = True
            #~ if product.routing_state == 'downloading' and product.vehicle_type == 'principal':
                #~ available = True
            #~ res.update( {product.id: available} )
        #~ return res
#~ 
    #~ _columns = {
            #~ 'routing_available':  fields.function(_get_routing_available, method=True, type="boolean", string="Available", fnct_search=_search_routing_available,),
        #~ }
#~ 
#~ product_product()


#~ class tire_history(osv.osv):
    #~ _name = 'tire.history'
#~ 
    #~ _rec_name = 'tracto_id'
    #~ _columns = {
            #~ 'tracto_id': fields.many2one('product.product', 'Tracto/Caja', required=True),
            #~ 'tire_id': fields.many2one('product.product', 'Tire', required=True),
            #~ 'date': fields.date('Fecha', required=True),
            #~ 'distance': fields.integer('Kilometraje'),
            #~ 'position': fields.char('Posicion', size=64)
        #~ }
#~ 
    #~ _defaults = {
            #~ 'date': lambda *a: time.strftime('%Y-%m-%d'),
        #~ }
#~ 
#~ tire_history()
