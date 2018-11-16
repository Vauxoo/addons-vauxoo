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
from openerp.osv import osv, fields
from openerp.addons.decimal_precision import decimal_precision as dp


class mrp_request_return(osv.TransientModel):
    _name = 'mrp.request.return'
    _columns = {
        're_line_ids': fields.one2many('mrp.request.return.line', 'wizard_id',
            'Acreation'),
        'type': fields.selection([('request', 'Request')], 'Type',
            required=True)
    }

    _defaults = {
        'type': 'request',
    }

    def action_request_return(self, cr, uid, ids, context={}):
        stock_picking = self.pool.get('stock.picking')
        mrp_production = self.pool.get('mrp.production')
        stock_move = self.pool.get('stock.move')

        mrp_ids = context.get('active_ids', [])
        production = self.pool.get('mrp.production').browse(
            cr, uid, mrp_ids, context=context)[0]

        for wizard_moves in self.browse(cr, uid, ids, context=context):
            if wizard_moves.type == 'request':
                context['type'] = wizard_moves.type
                pick_id = mrp_production._make_production_internal_shipment2(
                    cr, uid, production, context=context)
                stock_picking.write(cr, uid, pick_id, {
                                    'state': 'draft',
                                    'production_id': production.id})
                for wiz_move in wizard_moves.re_line_ids:
                    if wiz_move.product_qty > 0.0:
                        shipment_move_id = mrp_production._make_production_internal_shipment_line2(
                            cr, uid, production, wiz_move, pick_id, False)
                        mrp_production._make_production_consume_line(
                            cr, uid, wiz_move, False)

            if wizard_moves.type == 'return':
                context['type'] = wizard_moves.type
                pick_id_return = mrp_production._make_production_internal_shipment2(
                    cr, uid, production, context=context)
                stock_picking.write(cr, uid, pick_id_return, {
                                    'state': 'draft',
                                    'auto_picking': False,
                                    'production_id': production.id})
                for wiz_move2 in wizard_moves.re_line_ids:
                    if wiz_move2.product_qty > 0.0:
                        shipment_move_id = mrp_production._make_production_internal_shipment_line(
                            cr, uid, production, wiz_move2, pick_id_return,
                            parent_move_id=False,
                            destination_location_id=False)
                        stock_move.write(cr, uid, shipment_move_id, {
                                         'state': 'draft'})

        return {}

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(mrp_request_return, self).default_get(
            cr, uid, fields, context=context)
        mrp_ids = context.get('active_ids', [])
        if not mrp_ids or (not context.get('active_model') == 'mrp.production') \
                or len(mrp_ids) != 1:
            return res
        mrp_id, = mrp_ids
        if 're_line_ids' in fields:
            mrp = self.pool.get('mrp.production').browse(
                cr, uid, mrp_id, context=context)
            list_moves = []
            for m in mrp.product_lines:
                type_prod = m.product_id and m.product_id.type or ''
                if type_prod != 'service' and type_prod != '':
                    list_moves.append(m)
            moves = [self._partial_move_for(
                cr, uid, x, mrp) for x in list_moves]
            res.update(re_line_ids=moves)
        return res

    def _partial_move_for(self, cr, uid, move, production):
        partial_move = {
            'product_id': move.product_id.id,
            'product_qty': 0.0,
            'product_uom': move.product_uom.id,
            'product_uos_qty': move.product_uos and
            move.product_uos_qty or False,
            'product_uos': move.product_uos and
            move.product_uos.id or False,
            'location_id': production.location_src_id.id,
            'location_dest_id': production.location_src_id.id,
            'production_id': move.production_id.id
        }
        return partial_move


class mrp_request_return_line(osv.TransientModel):
    _name = 'mrp.request.return.line'
    _rec_name = 'product_id'

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(mrp_request_return_line, self).default_get(
            cr, uid, fields, context=context)
        mrp_ids = context.get('act_ids', [])
        if not mrp_ids or len(mrp_ids) != 1:
            return res
        mrp_id, = mrp_ids
        mrp = self.pool.get('mrp.production').browse(
            cr, uid, mrp_id, context=context)
        res.update({
            'location_id': mrp.location_src_id.id,
            'location_dest_id': mrp.location_src_id.id,
            'production_id': mrp.id})
        return res

    _columns = {
        'product_id': fields.many2one('product.product', string="Product",
            required=True),
        'product_qty': fields.float("Quantity",
            digits_compute=dp.get_precision('Product UoM'), required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure',
            required=True,),
        'location_id': fields.many2one('stock.location', 'Location',
            required=True),
        'location_dest_id': fields.many2one('stock.location', 'Dest. Location',
            required=True),
        'move_id': fields.many2one('stock.move', "Move"),
        'production_id': fields.many2one('mrp.production', 'Production'),
        'product_uos': fields.many2one('product.uom', 'Product UOS'),
        'product_uos_qty': fields.float('Quantity UoS'),
        'wizard_id': fields.many2one('mrp.request.return', string="Wizard"),
    }

    def on_change_product_uom(self, cr, uid, ids, product_id):
        product_product = self.pool.get('product.product')
        product = product_product.browse(cr, uid, product_id)
        return {'value': {'product_uom': product.uom_id and product.uom_id.id}}


class mrp_consume(osv.TransientModel):
    _inherit = 'mrp.consume'

    def action_consume(self, cr, uid, ids, lot_id=False, context=None):
        if context is None:
            context = {}
        context['type'] = 'request'
        mrp_ids = context.get('active_ids', [])
        stock_move_obj = self.pool.get('stock.move')
        mrp_production = self.pool.get('mrp.production')
        product_uom_pool = self.pool.get('product.uom')
        stock_picking = self.pool.get('stock.picking')
        mrp_consume_line = self.pool.get('mrp.consume.line')
        pick_id = 0
        production = mrp_production.browse(
            cr, uid, mrp_ids, context=context)[0]
        for move in self.browse(cr, uid, ids, context=context):
            for line in move.consume_line_ids:
                fetch_record = stock_move_obj.browse(
                    cr, uid, line.move_id.id, context=context)
                qty_to_consume = product_uom_pool._compute_qty(
                    cr, uid, line.product_uom.id, line.quantity,
                    to_uom_id=fetch_record.product_uom.id)
                current_qty = product_uom_pool._compute_qty(
                    cr, uid, fetch_record.product_uom.id,
                    fetch_record.product_qty,
                    to_uom_id=fetch_record.product_uom.id)
                if qty_to_consume > current_qty:
                    move_id = stock_move_obj.copy(cr, uid, line.move_id.id, {
                        'product_qty': qty_to_consume - current_qty})
                    mrp_production.write(cr, uid,
                                context.get('active_ids', False), {
                                    'move_lines': [(4, move_id)]}, context=context)
                    stock_move_obj.action_consume(cr, uid, [move_id],
                                                qty_to_consume - current_qty,
                                                line.location_id.id,
                                                lot_id=lot_id,
                                                context=context)
                    mrp_consume_line.write(cr, uid, line.id, {
                        'quantity': current_qty,
                        'product_uom': fetch_record.product_uom.id})

                    fetch_record.production_id = production
                    fetch_record.product_qty = qty_to_consume - current_qty
                    if not pick_id:
                        pick_id = mrp_production._make_production_internal_shipment2(
                            cr, uid, production, context=context)
                    stock_picking.write(cr, uid, pick_id, {
                                        'state': 'draft',
                                        'production_id': production.id})
                    shipment_move_id = mrp_production._make_production_internal_shipment_line(
                        cr, uid, fetch_record, pick_id, False)
        return super(mrp_consume, self).action_consume(cr, uid, ids, lot_id=lot_id, context)
