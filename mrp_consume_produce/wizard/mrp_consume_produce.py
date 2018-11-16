# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
#
#    Coded by: julio (julio@vauxoo.com)
#
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
#
from openerp.osv import osv, fields
from openerp.addons.decimal_precision import decimal_precision as dp
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
                if product_id in moves_grouped:
                    moves_grouped[product_id] += [move_id]
                else:
                    moves_grouped[product_id] = [move_id]
        return moves_grouped

    def _get_consume_lines_list(self, cr, uid, production_id, context=None):
        """
        Get the consume lines to create.
        @param production_id: manufacturing order id.
        @return: a list of dictionaries with the values for the consume
        lines to create
        """
        context = context or {}
        consume_line_ids = list()
        active_move_ids = self._get_active_move_ids(
            cr, uid, production_id, context=context)
        moves_dict = self._get_moves_grouped_by_product(
            cr, uid, active_move_ids, context=context)
        for move_ids in moves_dict.values():
            consume_line_ids += [self._get_consume_line_values(
                cr, uid, production_id, move_ids, context=context)]
        return consume_line_ids

    def _get_default_consume_line_ids(self, cr, uid, context=None):
        """
        Return the consume lines ids by default for the current work order lot
        """
        context = context or {}
        consume_line_ids = list()
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
        consume_line_ids = self._get_consume_lines_list(
            cr, uid, production_id, context=context)
        return consume_line_ids

    _columns = {
        'consume_line_ids': fields.one2many('mrp.consume.line',
                                            'wizard_id', 'Consume')
    }

    _defaults = {
        'consume_line_ids': _get_default_consume_line_ids,
    }

    def action_consume(self, cr, uid, ids, lot_id=False, context=None):
        context = context or {}
        uom_obj = self.pool.get('product.uom')
        for production in self.browse(cr, uid, ids, context=context):
            for consume_line in production.consume_line_ids:
                line_qty_left = consume_line.quantity
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

                        move_line.move_id.action_consume(
                            line_qty_left, move_line.location_id.id,
                            lot_id=lot_id, context=context)

                        move_apportionment_qty = uom_obj._compute_qty(
                            cr, uid, move_line.move_id.product_uom.id,
                            move_line.move_id.product_qty,
                            consume_line.product_uom.id)
                        line_qty_left -= move_apportionment_qty

        return {}

    #~ TODO: check this method, not used here but used in module
    #~ mrp_request_return
    def _partial_move_for(self, cr, uid, production_id, move_ids,
                          context=None):
        """
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

        partial_move = {
            'product_id': product_id,
            'quantity': product_qty,
            'product_uom': product_uom,
            'consume_line_move_ids':
            map(lambda move_line: (0, 0, move_line), consume_line_move_ids),
        }
        return partial_move

    def _get_active_move_ids(self, cr, uid, production_id, context=None):
        """
        Get the valid moves to be consume for a manufacturing order. That
        are those stock move that are not in Done or Cancel state.
        @param production_id: manufactuirng order id.
        @return: list of stock move ids that can ve consumed
        """
        context = context or {}
        production_obj = self.pool.get('mrp.production')
        move_brws = production_obj.browse(
            cr, uid, production_id, context=context).move_lines
        active_move_ids = [move_brw.id
                           for move_brw in move_brws
                           if move_brw.state not in ('done', 'cancel')]
        return active_move_ids

    def _get_consume_line_values(self, cr, uid, production_id, move_ids,
                                 context=None):
        """
        @param production_id: the production id where the wizard was called.
        @param move_ids: list of stock move id.
        @return: a dictionary of values to create a consume line.
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

    def _get_produce_line_list(self, cr, uid, production_id, context=None):
        """
        @param production_id: manufacturing order id.
        @return: a list of dictionaries values with the produce lines to
        create.
        """
        context = context or {}
        produce_line_list = list()
        active_move_ids = self._get_active_move_ids(
            cr, uid, production_id, context=context)
        for move_id in active_move_ids:
            produce_line_list += [self._get_produce_line_values(
                cr, uid, move_id, context=context)]
        return produce_line_list

    def _get_default_produce_line_ids(self, cr, uid, context=None):
        """
        Search the active stock moves from products to produce and then
        generate the list of dictionary values to create the produce line ids
        """
        context = context or {}
        production_obj = self.pool.get('mrp.production')
        produce_line_list = list()

        production_ids = context.get('active_ids', [])
        active_model = context.get('active_model', False)
        if not production_ids or len(production_ids) != 1:
            raise osv.except_osv(
                _('Error!!'),
                _('You need to call method using the wizard from the'
                  ' manufacturing order one by one.'))
        if active_model not in ['mrp.production']:
            raise osv.except_osv(
                _('Error!!'),
                _('You this wizard can be only called by the manufacturing'
                  ' order.'))
        production_id = production_ids[0]
        production_brw = production_obj.browse(
            cr, uid, production_id, context=context)

        produce_line_list = self._get_produce_line_list(
            cr, uid, production_id, context=context)
        return produce_line_list

    _columns = {
        'produce_line_ids': fields.one2many('mrp.produce.line',
                                            'produce_id', 'Consume')
    }

    _defaults = {
        'produce_line_ids': _get_default_produce_line_ids,
    }

    def _get_produce_line_values(self, cr, uid, move_id, context=None):
        """
        return the dictionary that fill the produce lines with the move values.
        @param move_id: move id.
        """
        context = context or {}
        move_obj = self.pool.get('stock.move')
        move_brw = move_obj.browse(cr, uid, move_id, context=context) or False
        if not move_id or not move_brw:
            raise osv.except_osv(
                _('Programming Error!'),
                _('You are not given a valid stock move id so this feature can'
                  ' be accomplished.'))
        values = {
            'product_id': move_brw.product_id.id,
            'quantity': move_brw.product_qty,
            'product_uom': move_brw.product_uom.id,
            'move_id': move_brw.id,
            'location_id': move_brw.location_id.id,
            'location_dest_id': move_brw.location_dest_id.id,
        }
        return values

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

    def _get_active_move_ids(self, cr, uid, production_id, context=None):
        """
        Get the valid moves to be produce for a manufacturing order. That
        are those stock move that are not in Done or Cancel state.
        @param production_id: manufactuirng order id.
        @return: list of stock move ids that can be produced
        """
        context = context or {}
        production_obj = self.pool.get('mrp.production')
        move_brws = production_obj.browse(
            cr, uid, production_id, context=context).move_created_ids
        active_move_ids = [move_brw.id
                           for move_brw in move_brws
                           if move_brw.state not in ('done', 'cancel')]
        return active_move_ids


class mrp_consume_line(osv.TransientModel):
    _name = 'mrp.consume.line'
    _rec_name = 'product_id'
    _columns = {
        'product_id': fields.many2one('product.product', string="Product",
                                      required=True),
        'quantity': fields.float("Quantity",
                                 digits_compute=dp.get_precision(
                                     'Product UoM'), required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure',
                                       required=True,),
        'consume_line_move_ids': fields.one2many(
            'mrp.consume.line.move',
            'consume_line_id',
            'Moves',
            required=True,
            help='Moves corresponding to the product in the consume line'),
        'wizard_id': fields.many2one('mrp.consume', string="Wizard"),
    }


class mrp_produce_line(osv.TransientModel):

    _name = 'mrp.produce.line'
    _rec_name = 'product_id'
    _columns = {
        'product_id': fields.many2one(
            'product.product',
            'Product',
            required=True,
            help='Product to be Produce'
        ),
        'quantity': fields.float(
            'Quantity',
            digits_compute=dp.get_precision('Product UoM'),
            required=True,
            help='Quantity that will be produced'
        ),
        'product_uom': fields.many2one(
            'product.uom',
            'Unit of Measure',
            required=True,
            help='Units of measure corresponding to the quantity'
        ),
        'move_id': fields.many2one('stock.move', "Move"),
        'location_id': fields.many2one(
            'stock.location',
            'Location',
            required=True
        ),
        'location_dest_id': fields.many2one(
            'stock.location',
            'Dest. Location',
            required=True
        ),
        'produce_id': fields.many2one(
            'mrp.produce',
            'Produce Wizard'
        ),
    }


class mrp_consume_line_move(osv.TransientModel):

    """
    This model refered to stock moves dummy data that is used in the
    mrp_consume_line model.
    """

    _name = 'mrp.consume.line.move'
    _description = 'MRP Consume Line Move'
    _columns = {
        'consume_line_id': fields.many2one(
            'mrp.consume.line',
            'Consume Line'),
        'move_id': fields.many2one(
            'stock.move',
            'Move'),
        'location_id': fields.many2one(
            'stock.location',
            'Location',
            required=True),
        'location_dest_id': fields.many2one(
            'stock.location',
            'Dest. Location',
            required=True),
    }
