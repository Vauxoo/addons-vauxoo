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
from openerp.osv import osv, fields
import decimal_precision as dp
from openerp.tools.translate import _


class mrp_consume(osv.TransientModel):
    _name = 'mrp.consume'
    _columns = {
        'consume_line_ids': fields.one2many('mrp.consume.line',
            'wizard_id', 'Consume')
    }

    def action_consume(self, cr, uid, ids, context={}):
        for production in self.browse(cr, uid, ids, context=context):
            for raw_product in production.consume_line_ids:
                context.update({
                    'product_uom': raw_product.product_uom.id,
                    'product_uom_move': raw_product.move_id.product_uom.id,
                    'quantity': raw_product.quantity})
                for move_line in raw_product.consume_line_move_ids:
                    move_line.move_id.action_consume(
                        raw_product.quantity, move_line.location_id.id,
                        context=context)

        return {}

    def default_get(self, cr, uid, fields, context=None):
        context = context or {}
        production_obj = self.pool.get('mrp.production')
        res = super(mrp_consume, self).default_get(
            cr, uid, fields, context=context)
        production_ids = context.get('active_ids', [])
        if (not production_ids
            or (not context.get('active_model') == 'mrp.production')
            or len(production_ids) != 1):
            return res
        production_id = production_ids[0]
        if 'consume_line_ids' in fields:
            production_brw = production_obj.browse(cr, uid, production_id,
                                                   context=context)
            moves = \
                [self._partial_move_for(cr, uid, move_brw.id, context=context)
                 for move_brw in production_brw.move_lines
                 if move_brw.state not in ('done', 'cancel')]
            res.update(consume_line_ids=moves)
        return res

    def _partial_move_for(self, cr, uid, move_id, context=None):
        """
        @param move_id: stock move id. 
        """
        context = context or {}
        move_obj = self.pool.get('stock.move')
        move_brw = move_obj.browse(cr, uid, move_id, context=context)
        partial_move = {
            'product_id': move_brw.product_id.id,
            'quantity': move_brw.product_qty,
            'product_uom': move_brw.product_uom.id,
            'prodlot_id': move_brw.prodlot_id.id,
            'move_id': move_brw.id,
            'location_id': move_brw.location_id.id,
            'location_dest_id': move_brw.location_dest_id.id,
        }
        return partial_move


class mrp_produce(osv.TransientModel):
    _name = 'mrp.produce'
    _columns = {
        'produce_line_ids': fields.one2many('mrp.consume.line',
            'wizard2_id', 'Consume')
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(mrp_produce, self).default_get(
            cr, uid, fields, context=context)
        mrp_ids = context.get('active_ids', [])
        if not mrp_ids or (not context.get('active_model') == 'mrp.production') \
                or len(mrp_ids) != 1:
            return res
        mrp_id, = mrp_ids
        if 'produce_line_ids' in fields:
            mrp = self.pool.get('mrp.production').browse(
                cr, uid, mrp_id, context=context)
            moves = [self.pool.get('mrp.consume')._partial_move_for(cr, uid, m, context=context) \
                    for m in mrp.move_created_ids if m.state\
                    not in ('done', 'cancel')]
            res.update(produce_line_ids=moves)
        return res

    def action_produce(self, cr, uid, ids, context={}):
        for production in self.browse(cr, uid, ids, context=context):
            for raw_product in production.produce_line_ids:
                context.update({
                    'product_uom': raw_product.product_uom.id,
                    'product_uom_move': raw_product.move_id.product_uom.id,
                    'quantity': raw_product.quantity})
                raw_product.move_id.action_consume(
                    raw_product.quantity, raw_product.location_id.id,
                    context=context)
        return {}


class mrp_consume_line(osv.TransientModel):
    _name = 'mrp.consume.line'
    _rec_name = 'product_id'
    _columns = {
        'product_id': fields.many2one('product.product', string="Product",
            required=True),
        'quantity': fields.float("Quantity",
            digits_compute=dp.get_precision('Product UoM'), required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure',
            required=True,),
        'consume_line_move_ids': fields.one2many(
            'mrp.consume.line.move',
            'consume_line_id',
            _('Moves'),
            required=True,
            help=_('Moves corresponding to the product in the consume line')),
        'wizard_id': fields.many2one('mrp.consume', string="Wizard"),
        'wizard2_id': fields.many2one('mrp.produce', string="Wizard"),
    }


class mrp_consume_line_move(osv.TransientModel):

    """
    This model refered to stock moves dummy data that is used in the
    mrp_consume_line model.
    """

    _name = 'mrp.consume.line.move'
    _description = _('MRP Consume Line Move')
    _columns = {
        'consume_line_id': fields.many2one(
            'mrp.consume.line',
            _('Consume Line')),
        'move_id': fields.many2one(
            'stock.move',
            _('Move')),
        'location_id': fields.many2one(
            'stock.location',
            _('Location'),
            required=True),
        'location_dest_id': fields.many2one(
            'stock.location',
            _('Dest. Location'),
            required=True),
    }
