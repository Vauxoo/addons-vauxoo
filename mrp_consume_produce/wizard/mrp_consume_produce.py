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

    def _get_moves_grouped_by_product(self, cr, uid, move_ids,
                                      context=None):
        """
        Return a dictionary with a list of the moves corresponding by
        product {product: [move_ids]}.
        @param move_ids: list of move ids.
        """
        context = context or {}
        moves_grouped = dict()
        move_obj = self.pool.get('stock.move')
        move_data_list = map(
            lambda move_brw: {move_brw.product_id.id: move_brw.id},
            move_obj.browse(cr, uid, move_ids, context=context))

        for move_data in move_data_list:
            for (product_id, move_id) in move_data.iteritems():
                if moves_grouped.has_key(product_id):
                    moves_grouped[product_id] += [move_id]
                else:
                    moves_grouped[product_id] = [move_id]
        return moves_grouped

    def _get_default_consume_line_ids(self, cr, uid, context=None):
        """
        Return the consume lines ids by default for the current work order lot
        """
        context = context or {}
        consume_line_ids = list()
        production_obj = self.pool.get('mrp.production')
        wol_obj = self.pool.get('mrp.workorder.lot')
        # getting the production_id
        production_ids = context.get('active_ids', [])
        active_model = context.get('active_model', False)
        if not production_ids or len(production_ids) != 1:
            raise osv.except_osv(
                _('Error!!'),
                _('You need to call method using the wizard, one by one per'
                  ' manufacturing order or by an active work order lot.'))
        if active_model not in ['mrp.production', 'mrp.workorder.lot']:
            raise osv.except_osv(
                _('Error!!'),
                _('You this wizard can be only called by the manufacturing'
                  ' order or by an active work order lot.'))
        production_id = active_model == 'mrp.production' \
            and production_ids[0] or wol_obj.browse(
                cr, uid, production_ids,
                context=context)[0].production_id.id
        # getting active move ids grouped by product
        move_brws = production_obj.browse(
            cr, uid, production_id, context=context).move_lines
        active_move_ids = [move_brw.id
                           for move_brw in move_brws
                           if move_brw.state not in ('done', 'cancel')]
        moves_of = \
            self._get_moves_grouped_by_product(
                cr, uid, active_move_ids, context=context)
        #~ update consume lines data
        for move_ids in moves_of.values():
            consume_line_ids += [self._get_consume_line_dict(
                cr, uid, production_id, move_ids, context=context)]
        return consume_line_ids

    _columns = {
        'consume_line_ids': fields.one2many('mrp.consume.line',
            'wizard_id', 'Consume')
    }

    _defaults = {
        'consume_line_ids': _get_default_consume_line_ids,
    }

    def action_consume(self, cr, uid, ids, context=None):
        context = context or {}
        uom_obj = self.pool.get('product.uom')
        for production in self.browse(cr, uid, ids, context=context):
            for consume_line in production.consume_line_ids:
                line_qty_left = consume_line.quantity

                print '\n'*3, 'consume_line', (
                    consume_line.product_id.name_template, line_qty_left)

                for move_line in consume_line.consume_line_move_ids:
                    if line_qty_left >= 0.0:
                        context.update({
                            'product_uom': consume_line.product_uom.id,
                            'product_uom_move':
                            move_line.move_id.product_uom.id,
                            'quantity': line_qty_left})
                        # TODO: this 'quantity': line_qty_left could be change
                        # becuase wath happend when products to consume moves
                        # are in different uom (test with mrp_request_return)

                        print 'move.action_consume(%s)' % (
                            context['quantity'],)

                        move_line.move_id.action_consume(
                            line_qty_left, move_line.location_id.id,
                            context=context)

                        move_apportionment_qty = uom_obj._compute_qty(
                            cr, uid, move_line.move_id.product_uom.id,
                            move_line.move_id.product_qty,
                            consume_line.product_uom.id)
                        line_qty_left -= move_apportionment_qty

                        print (
                            'move', move_line.move_id.id,
                            'real qty', move_line.move_id.product_qty,
                            move_line.move_id.product_uom.name,
                            'to_line_oum qty', move_apportionment_qty,
                            consume_line.product_uom.name,
                            'line_qty_left', line_qty_left)
        return {}

    def default_get(self, cr, uid, fields, context=None):
        #~ TODO: delete this method. only to print the information of the default. for control in the debuging fase.

        context = context or {}
        res = super(mrp_consume, self).default_get(
            cr, uid, fields, context=context)

        import pprint
        print '\n'*3
        print '----'*20
        print 'mrp_consume_produce > mrp_consume.default_get()'
        print 'fields', fields
        print 'context',
        pprint.pprint(context)
        print 'res',
        pprint.pprint(res)
        print '----'*20
        print '\n'*3

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

    def _get_consume_line_dict(self, cr, uid, production_id, move_ids,
                               context=None):
        """
        @param production_id: the production id where the wizard was called.
        @param move_ids: list of stock move id.
        @return: a dictionary of values for a consume/produce line.
        """
        context = context or {}
        product_id = self._get_consume_line_product_id(
            cr, uid, move_ids, context=context)
        product_uom = self._get_consume_line_uom_id(
            cr, uid, production_id, product_id, context=context) 
        product_qty = self._get_consume_line_product_qty(
            cr, uid, move_ids, product_uom, context=context)
        consume_line_move_ids = self._get_consume_line_move_ids(
            cr, uid, move_ids, context=context)

        consume_line_dict = {
            'product_id': product_id,
            'product_uom': product_uom,
            'quantity': product_qty,
            'consume_line_move_ids':
            map(lambda move_line: (0, 0, move_line), consume_line_move_ids),
        }
        return consume_line_dict

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
        'produce_line_ids': fields.one2many('mrp.produce.line',
            'produce_id', 'Consume')
    }

    def _get_produce_line_values(self, cr, uid, move_id, context=None):
        """
        return the dictionary that fill the produce lines with the move values.
        @param move_id: move id.
        """
        context = context or {}
        move_obj = self.pool.get('stock.move')
        move_brw = move_obj.browse(cr, uid, move_id, context=context)
        values = {
            'product_id': move_brw.product_id.id,
            'quantity': move_brw.product_qty,
            'product_uom': move_brw.product_uom.id,
            'prodlot_id': move_brw.prodlot_id.id,
            'move_id': move_brw.id,
            'location_id': move_brw.location_id.id,
            'location_dest_id': move_brw.location_dest_id.id,
        }
        return values

    def default_get(self, cr, uid, fields, context=None):
        context = context or {}
        production_obj = self.pool.get('mrp.production')
        res = super(mrp_produce, self).default_get(
            cr, uid, fields, context=context)
        production_ids = context.get('active_ids', [])
        if not production_ids or (not context.get('active_model') == 'mrp.production') \
                or len(production_ids) != 1:
            return res
        production_id = production_ids[0]

        if 'produce_line_ids' in fields:
            production_brw = production_obj.browse(
                cr, uid, production_id, context=context)
            moves = \
                [self._get_produce_line_values(
                    cr, uid, move_brw.id, context=context)
                 for move_brw in production_brw.move_created_ids
                 if move_brw.state not in ('done', 'cancel')]
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


class mrp_produce_line(osv.TransientModel):

    _name = 'mrp.produce.line'
    _rec_name = 'product_id'
    _columns = {
        'product_id': fields.many2one(
            'product.product',
            _('Product'),
            required=True,
            help=_('Product to be Produce')),
        'quantity': fields.float(
            _('Quantity'),
            digits_compute=dp.get_precision('Product UoM'),
            required=True,
            help=_('Quantity that will be produced'),
            ),
        'product_uom': fields.many2one(
            'product.uom',
            _('Unit of Measure'),
            required=True,
            help=_('Units of measure corresponding to the quantity')),
        'move_id': fields.many2one('stock.move', "Move"),
        'location_id': fields.many2one(
            'stock.location',
            _('Location'),
            required=True),
        'location_dest_id': fields.many2one(
            'stock.location',
            _('Dest. Location'),
            required=True),
        'produce_id': fields.many2one(
            'mrp.produce',
            _('Produce Wizard')),
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
