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
from mx.DateTime import *
import netsvc

class tracto_modelo(osv.osv):
    _name = 'tracto.modelo'

    _columns = {
            'name': fields.char('Modelo', size=64, required=True),
            'description': fields.char('Descripcion', size=64),
            'line_ids': fields.one2many('maintenance.bom', 'modelo_id', 'Lista de Mantenimiento')
        }

tracto_modelo()

class product_product(osv.osv):
    _inherit = 'product.product'

    _columns = {
            'modelo_id': fields.many2one('tracto.modelo', 'Modelo'),
            'distance': fields.float('Kilometraje'),
            'maintenance_ids': fields.one2many('maintenance.order.line', 'product_id', 'Programa de Mantenimientos')
        }

product_product()

class maintenance_bom(osv.osv):
    _name = 'maintenance.bom'

    def _get_costo(self, cr, uid, ids, name, args, context):
        res = {}
        for bom in self.browse(cr, uid, ids):
            res[bom.id] = 0
            for line in bom.line_ids:
                res[bom.id] += (line.costo*line.product_qty)
        return res

    _columns = {
            'name': fields.char('Descripcion', size=128, required=True),
            'modelo_id': fields.many2one('tracto.modelo', 'Modelo'),
            'line_ids': fields.one2many('maintenance.bom.line', 'bom_id', 'Lineas'),
            'notes': fields.text('Notas'),
            'tiempo': fields.float('Horas Estimadas'),
            'costo_total': fields.function(_get_costo, method=True, type='float', string='Costo total'),
            'type': fields.selection([('',''),('week','Semanas'),('mes', 'Meses'),('km', 'KM')], 'Tipo'),
            'type_qty': fields.integer('Cantidad'),
            'active': fields.boolean('Active')
        }

    _defaults = {
        'active': lambda *a: True,
        }

maintenance_bom()

class maintenance_bom_line(osv.osv):
    _name = 'maintenance.bom.line'

    def _get_total(self, cr, uid, ids, name, args, context):
        query = """SELECT mbl.id, product_qty*costo FROM maintenance_bom_line mbl WHERE id IN (%s)"""%",".join(map(str, ids))
        cr.execute(query)
        res = dict(cr.fetchall())
        for id in ids:
            res.setdefault(id, 0.0)
        return res

    _rec_name = 'product_id'

    _columns = {
            'product_id': fields.many2one('product.product', 'Producto', required=True, domain = [('type','=','product')]),
            'product_qty': fields.float('Cantidad', required=True),
            'costo': fields.float('Costo'),
            'total': fields.function(_get_total, method=True, type='float', string="Total"),
            'bom_id': fields.many2one('maintenance.bom', 'Lista de Mantenimiento', ondelete='cascade', select=True),
            'product_uom': fields.many2one('product.uom', 'UoM', required=True),
        }

    def onchange_product(self, cr, uid, ids, product_id):
        if not product_id:
            return {'value':{'product_uom':False, 'costo':0}}
        product = self.pool.get('product.product').browse(cr, uid, product_id)
        return {'value':{'product_uom':product.uom_id.id, 'name': product.name, 'costo':product.standard_price}}

maintenance_bom_line()

class maintenance_order_line(osv.osv):
    _name = 'maintenance.order.line'

    def create(self, cr, uid, vals, context={}):
        query = "SELECT COALESCE(MAX(orden)+1, 1) FROM maintenance_order_line WHERE date = '%s'"%vals['date']
        cr.execute(query)
        res = cr.fetchone()[0]
        vals['orden'] = res
        return super(maintenance_order_line, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.has_key('date'):
            query = "SELECT COALESCE(MAX(orden)+1, 1) FROM maintenance_order_line WHERE date = '%s'"%vals['date']
            cr.execute(query)
            res = cr.fetchone()[0]
            vals['orden'] = res
        return super(maintenance_order_line, self).write(cr, uid, ids, vals, context)

    def _get_costo(self, cr, uid, ids, name, args, context):
        res = {}
        for order in self.browse(cr, uid, ids):
            res[order.id] = 0
            for line in order.material_ids:
                res[order.id] += line.total
        return res

    _columns = {
            'name': fields.char('Descripcion', size=128, required=True, readonly=True, states={'draft':[('readonly', False)]}),
            'orden': fields.integer('Orden del Dia', readonly=True),
            'product_id': fields.many2one('product.product', 'Tracto', required=True, readonly=True, states={'draft':[('readonly', False)]}),
            'bom_id': fields.many2one('maintenance.bom', 'Lista de Mantenimiento', readonly=True, states={'draft':[('readonly', False)]}),
            'priority': fields.integer('Prioridad'),
            'date':fields.date('Fecha Reporte', required=True, readonly=True, states={'draft':[('readonly', False)]}),
            'date_done':fields.date('Fecha Realizado', readonly=True),
            'date_due': fields.date('Fecha Compromiso', readonly=True),
            'date_release': fields.datetime('Fecha Termino'),
            'notes': fields.text('Description'),
            'costo': fields.function(_get_costo, method=True, type='float', string='Costo total'),
            'warehouse_id': fields.many2one('stock.warehouse', 'Almacen'),
            'picking_ids': fields.one2many('stock.picking', 'maintenance_id', 'Traspasos'),
            'type':fields.selection([
                ('correctivo','Correctivo'),
                ('preventivo','Preventivo'), ], 'Tipo'),
            'state':fields.selection([
                ('draft','Sin Realizar'),
                ('done','Terminado'),
                ('cancel', 'Cancelado'),
                ('in_progress','En Proceso'),
                ('reassigned','Reasignado')], 'State', readonly=True),
            'material_ids': fields.one2many('maintenance.material.line', 'line_id', 'Materiales'),
            'modelo_id': fields.many2one('tracto.modelo', 'Modelo'),
            'pendiente_id': fields.many2one('maintenance.order.line', 'Pendiente', readonly=True),
            'distance': fields.float('Kilometraje', required=True, readonly=False, states={'draft':[('readonly', False)]}),
        }

    _defaults = {
        'state': lambda *a: 'draft',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'type': lambda *a: 'preventivo',
        }

    def action_start(self, cr, uid, ids, ctx={}):
        self.write(cr, uid, ids, {'state':'in_progress'})
        return True

    def onchange_bom(self, cr, uid, ids, bom_id):
        if not bom_id:
            return {'value':{}}
        bom = self.pool.get('maintenance.bom').browse(cr, uid, bom_id)
        return {'value':{'name':bom.name}}

    def onchange_product(self, cr, uid, ids, product_id):
        if not product_id:
            return {'value':{'modelo_id':False, 'bom_id':False}}
        product = self.pool.get('product.product').browse(cr, uid, product_id)
        return {'value':{'modelo_id':product.modelo_id and product.modelo_id.id or False, 'distance':product.distance}}

    def action_done(self, cr, uid, ids, ctx={}):
        self.write(cr, uid, ids, {'state':'done', 'date_done':time.strftime('%Y-%m-%d')})
        picking_obj = self.pool.get('stock.picking')
        picking_id = False
        for maintenance in self.browse(cr, uid, ids):
            self.write(cr, uid, maintenance.id, {'distance':maintenance.product_id.distance})
            if maintenance.material_ids:
                picking_id = picking_obj.create(cr, uid, {
                    'origin': 'MA:%s'%maintenance.name,
                    'type': 'internal',
                    'move_type': 'one',
                    'state': 'assigned',
                    'maintenance_id': maintenance.id,
                    'auto_picking': False,})
            for line in maintenance.material_ids:
                self.pool.get('stock.move').create(cr, uid, {
                        'name':'%s'%line.product_id.name,
                        'picking_id':picking_id,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'product_uom': line.product_id.uom_id.id,
                        'date_planned': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'location_id': maintenance.warehouse_id.lot_stock_id.id,
                        'location_dest_id': maintenance.warehouse_id.lot_output_id.id,
                        'state': 'draft',})
        if picking_id:
            picking_obj.draft_validate(cr, uid, [picking_id], ctx)
        return True

    def action_cancel(self, cr, uid, ids, ctx={}):
        self.write(cr, uid, ids, {'state':'cancel'})
        return True

    def action_draft(self, cr, uid, ids, ctx={}):
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    def action_calcular(self, cr, uid, ids, ctx={}):
        for order in self.browse(cr, uid, ids):
            if order.bom_id:
                self.pool.get('maintenance.material.line').unlink(cr, uid, map(lambda x: x.id, order.material_ids))
                for line in order.bom_id.line_ids:
                    self.pool.get('maintenance.material.line').create(cr, uid, {
                            'product_id': line.product_id.id,
                            'line_id': order.id,
                            'product_qty': line.product_qty,
                            'product_uom': line.product_uom.id,
                            'costo': line.costo,
                        })
        return True

    def _check_maintenance(self, cr, uid, ids):
        product_obj = self.pool.get('product.product')
        tracto_ids = product_obj.search(cr, uid, [])
        mol_ids = []
        for tracto in product_obj.browse(cr, uid, tracto_ids):
            if tracto.modelo_id:
                for bom in tracto.modelo_id.line_ids:
                    crear = False
                    res = self.search(cr, uid, [('product_id','=',tracto.id),('bom_id','=',bom.id)])
                    if not res and bom.type != '' and ( (bom.type == 'km' and tracto.distance > bom.type_qty) or bom.type != 'km'):
                        crear = True
                    else:
                        query = """SELECT CASE WHEN mb.type = 'km' THEN (pp.distance - MAX(mol.distance)) > type_qty
                                        WHEN mb.type = 'mes' THEN now() > MAX(date_done)+(type_qty||'months')::interval
                                        WHEN mb.type = 'mes' THEN now() > MAX(date_done)+(type_qty||'weeks')::interval
                                        ELSE False END as diferencia
                                    FROM maintenance_order_line mol
                                    JOIN maintenance_bom mb ON mol.bom_id = mb.id
                                    JOIN product_product pp ON pp.id = mol.product_id
                                    JOIN product_template pt ON pt.id = pp.product_tmpl_id
                                    WHERE product_id = %s AND mb.active = True AND mb.id = %s AND mol.state IN ('done', 'in_progress', 'draft')
                                    GROUP BY bom_id, mb.type, mb.type_qty, pp.distance"""%(tracto.id, bom.id)
                        cr.execute(query)
                        res = cr.dictfetchall()
                        for result in res:
                            if result['diferencia']:
                                crear = True
                    if crear:
                        mol_id = self.pool.get('maintenance.order.line').create(cr, uid, {
                            'name': bom.name,
                            'product_id':tracto.id,
                            'bom_id':bom.id,
                            'date': time.strftime('%Y-%m-%d'),
                            'modelo_id': tracto.modelo_id.id,
                            'distance': tracto.distance})
                        mol_ids.append(mol_id)
        return mol_ids

maintenance_order_line()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    _columns = {
            'maintenance_id': fields.many2one('maintenance.order.line', 'Programa de Mantenimientos', readonly=True),
        }

stock_picking()

class maintenance_material_line(osv.osv):
    _name = 'maintenance.material.line'
    _description = 'maintenance.material.line'

    def _get_total(self, cr, uid, ids, name, args, context):
        query = """SELECT mml.id, product_qty*costo FROM maintenance_material_line mml WHERE id IN (%s)"""%",".join(map(str, ids))
        cr.execute(query)
        res = dict(cr.fetchall())
        for id in ids:
            res.setdefault(id, 0.0)
        return res

    _rec_name = 'product_id'

    _columns = {
            'product_id': fields.many2one('product.product', 'Producto', required=True, domain=[('type', '!=', 'service')]),
            'line_id': fields.many2one('maintenance.order.line', 'Order Line'),
            'product_qty': fields.float('Cantidad'),
            'costo': fields.float('Costo'),
            'total': fields.function(_get_total, method=True, type='float', string="Total"),
            'product_uom': fields.many2one('product.uom', 'UoM'),
        }

    def onchange_product(self, cr, uid, ids, product_id):
        if not product_id:
            return {'value':{'product_uom':False, 'costo':0}}
        product = self.pool.get('product.product').browse(cr, uid, product_id)
        return {'value':{'product_uom':product.uom_id.id, 'name': product.name, 'costo':product.standard_price}}

maintenance_material_line()
