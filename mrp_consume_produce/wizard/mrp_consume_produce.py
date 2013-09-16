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
        move_obj = self.pool.get('stock.move')
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
            moves_brw = production_brw.move_lines
            moves_ld = map(lambda x: {x.product_id.id: x.id}, moves_brw)
            moves_of = dict()
            for move_data in moves_ld:
                for (product_id, move_id) in move_data.iteritems():
                    if moves_of.has_key(product_id):
                        moves_of[product_id] += [move_id] 
                    else:
                        moves_of[product_id] = [move_id] 

            for move_ids in moves_of.values():
                active_move_ids = \
                    [move_brw.id
                     for move_brw in (move_obj.browse(
                        cr, uid, move_ids, context=context))
                     if move_brw.state not in ('done', 'cancel')]
                moves = self._partial_move_for(
                    cr, uid, production_id, active_move_ids, context=context)
            res.update({'consume_line_ids': moves})

        return res

    def _partial_move_for(self, cr, uid, production_id, move_ids,
                          context=None):
        """
        @param move_ids: list of stock move id.
        @return: a dictionary of values for a consume/produce line.
        """
        context = context or {}
        move_obj = self.pool.get('stock.move')

        product_id = self._get_consume_line_product_id(
            cr, uid, move_ids, context=context)
        product_uom = self._get_consume_line_uom_id(
            cr, uid, production_id, product_id, context=context) 
        product_qty = self._get_consume_line_product_qty(
            cr, uid, move_ids, product_uom, context=context)
        prodlot_id = self._get_consume_line_prodlot_id(
            cr, uid, product_id, move_ids, context=context)
        consume_line_move_ids = self._get_consume_line_move_ids(
            cr, uid, move_ids, context=context)

        partial_move = {
            'product_id': product_id,
            'quantity': product_qty,
            'product_uom': product_uom,
            'prodlot_id': prodlot_id,
            'consume_line_move_ids':
            map(lambda move_line: (0, 0, move_line), consume_line_move_ids),
        }
        return partial_move

    def _get_consume_line_product_id(self, cr, uid, move_ids, context=None):
        """
        It gets a list of move ids and check that have the same product_id. If
        this condition is True return the product_id, else it raise an
        exception indicating that the moves correspond to different products
        and can be use to create one mrp.comsume.line.
        @param move_ids: stock move ids list to check.
        """
        context = context or {}
        move_obj = self.pool.get('stock.move')
        move_brws = move_obj.browse(cr, uid, move_ids, context=context)
        product_ids = [move_brw.product_id.id for move_brw in move_brws]
        if len(set(product_ids)) != 1:
            raise osv.except_osv(
                _('Error!'),
                _('You are trying to create a cosume line for two or more'
                  ' different products.'),
            )
        return product_ids[0]

    def _get_consume_line_uom_id(self, cr, uid, production_id, product_id,
                                 context=None):
        """
        Return the manufacturing order scheduled product uom defined for the
        given product.
        @param production_id: manufacturing order id.
        @param product_id: raw material product id.
        """
        context = context or {}
        production_brw = self.pool.get('mrp.production').browse(
            cr, uid, production_id, context=context)
        uom_id = [product_line.product_uom.id
                  for product_line in production_brw.product_lines
                  if product_line.product_id.id == product_id][0]            
        return uom_id

    def _get_consume_line_product_qty(self, cr, uid, move_ids, product_uom_id,
                                      context=None):
        """
        Return the summatory of every move given in move_ids.
        @param move_ids: stock move ids list to check.
        """
        context = context or {}
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        move_brws = move_obj.browse(cr, uid, move_ids, context=context)
        qty = \
            sum([uom_obj._compute_qty(
                    cr, uid, move_brw.product_uom.id, move_brw.product_qty,
                    product_uom_id)
                 for move_brw in move_brws])
        return qty

    def _get_consume_line_prodlot_id(self, cr, uid, product_id, move_ids,
                                     context=None):
        """
        Return the first production lot id found for the given product.
        @param product_id: product id.
        """
        context = context or {}
        move_obj = self.pool.get('stock.move')
        prodlot_obj = self.pool.get('stock.production.lot')
        move_brws = move_obj.browse(cr, uid, move_ids, context=context)
        prodlot_ids = \
            prodlot_obj.search(
                cr, uid, [('product_id', '=', product_id)], context=context) \
                or False
        # Note: First my intention was to use the move_brw.prodlot_id to get
        # the prodlot_id but this field is not set, I imagine that is set
        # before the move is consumed.
        return prodlot_ids and prodlot_ids[0] or False

    def _get_consume_line_move_ids(self, cr, uid, move_ids, context=None):
        """
        Return a list of dictonary with consume line move to create for the
        moves given.
        @param move_ids: move ids list that will be convert into consume line
                         moes.
        """
        context = context or {}
        move_obj = self.pool.get('stock.move')
        values = list()
        for move_brw in move_obj.browse(cr, uid, move_ids, context=context):
            values.append({
                'move_id': move_brw.id,
                'location_id': move_brw.location_id.id,
                'location_dest_id': move_brw.location_dest_id.id,
            })
        return values

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

        raise osv.except_osv(
            _('Alert'),
            _('This functionality is still in development.'))

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
