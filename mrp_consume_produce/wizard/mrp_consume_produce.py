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

class mrp_consume_line(osv.osv_memory):
    _name='mrp.consume.line'
    _rec_name = 'product_id'
    _columns = {
        'product_id' : fields.many2one('product.product', string="Product", required=True),
        'quantity' : fields.float("Quantity", digits_compute=dp.get_precision('Product UoM'), required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', required=True,),
        'location_id': fields.many2one('stock.location', 'Location', required=True),
        'location_dest_id': fields.many2one('stock.location', 'Dest. Location', required=True),
        'move_id' : fields.many2one('stock.move', "Move"),
        'wizard_id' : fields.many2one('mrp.consume', string="Wizard"),
    }

class mrp_produce_line(osv.osv_memory):
    _name='mrp.produce.line'
    _inherit = 'mrp.consume.line'


class mrp_produce(osv.osv_memory):
    _name='mrp.produce'
    _columns={
        'produce_line_ids' : fields.one2many('mrp.produce.line', 'wizard_id', 'Produce')
    }
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(mrp_produce, self).default_get(cr, uid, fields, context=context)
        mrp_ids = context.get('active_ids', [])
        if not mrp_ids or (not context.get('active_model') == 'mrp.production') \
            or len(mrp_ids) != 1:
            return res
        mrp_id, = mrp_ids
        if 'produce_line_ids' in fields:
            mrp = self.pool.get('mrp.production').browse(cr, uid, mrp_id, context=context)
            moves = [self.pool.get('mrp.consume')._partial_move_for(cr, uid, m) for m in mrp.move_created_ids if m.state not in ('done','cancel')]
            res.update(produce_line_ids=moves)
        return res

    def action_produce(self,cr,uid,ids,context={}):
        for production in self.browse(cr,uid,ids,context=context):
            for raw_product in production.produce_line_ids:
                context.update({'product_uom':raw_product.product_uom.id,
                    'product_uom_move':raw_product.move_id.product_uom.id,
                    'quantity':raw_product.quantity})
                raw_product.move_id.action_consume(raw_product.quantity, raw_product.location_id.id, context=context)
        return {}


class mrp_consume(osv.osv_memory):
    _name='mrp.consume'
    _columns={
        'consume_line_ids' : fields.one2many('mrp.consume.line','wizard_id','Consume')
    }
    def action_consume(self,cr,uid,ids,context={}):
        for production in self.browse(cr,uid,ids,context=context):
            for raw_product in production.consume_line_ids:
                context.update({'product_uom':raw_product.product_uom.id,
                    'product_uom_move':raw_product.move_id.product_uom.id,
                    'quantity':raw_product.quantity})
                raw_product.move_id.action_consume(raw_product.quantity, raw_product.location_id.id, context=context)
        return {}
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(mrp_consume, self).default_get(cr, uid, fields, context=context)
        mrp_ids = context.get('active_ids', [])
        if not mrp_ids or (not context.get('active_model') == 'mrp.production') \
            or len(mrp_ids) != 1:
            return res
        mrp_id, = mrp_ids
        if 'consume_line_ids' in fields:
            mrp = self.pool.get('mrp.production').browse(cr, uid, mrp_id, context=context)
            moves = [self._partial_move_for(cr, uid, m) for m in mrp.move_lines if m.state not in ('done','cancel')]
            res.update(consume_line_ids=moves)
        return res

    def _partial_move_for(self, cr, uid, move):
        partial_move = {
            'product_id' : move.product_id.id,
            'quantity' : move.product_qty,
            'product_uom' : move.product_uom.id,
            #'prodlot_id' : move.prodlot_id.id,
            'move_id' : move.id,
            'location_id' : move.location_id.id,
            'location_dest_id' : move.location_dest_id.id,
        }
        return partial_move
    
mrp_consume()
mrp_produce()
mrp_consume_line()
mrp_produce_line()
