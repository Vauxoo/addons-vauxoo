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
from openerp.tools.translate import _

import openerp.netsvc as netsvc


class mrp_production(osv.Model):
    _inherit = 'mrp.production'

    def _check_boolean(self, cr, uid, ids, field_name, args, context={}):
        res = {}
        for production in self.browse(cr, uid, ids, context=context):
            moves = [move for move in production.move_lines]
            if len(moves) == 0 and production.state != 'draft':
                res[production.id] = True
            else:
                res[production.id] = False
        return res

    def _check_len_move(self, cr, uid, ids, field_name, args, context={}):
        res = {}
        for production in self.browse(cr, uid, ids, context=context):
            moves = [move
                     for move in production.move_lines2
                     if move.state == 'done']
            res[production.id] = len(moves)
        return res

    def _check_len_move_prod(self, cr, uid, ids, field_name, args, context={}):
        res = {}
        for production in self.browse(cr, uid, ids, context=context):
            res[production.id] = len(production.move_created_ids2)
        return res

    def _check_move_lines2(self, cr, uid, ids, field_name, args, context={}):
        res = {}
        for production in self.browse(cr, uid, ids, context=context):
            moves = [move for move in production.move_lines2]
            res[production.id] = len(moves)
        return res

    _columns = {
        'consumed': fields.function(
            _check_boolean, string='consumed?',
            type='boolean',
            help="indicates if product to consume have been consumed\
                or canceled"),
        'len_move': fields.function(
            _check_len_move, string='moves',
            type='float'),
        'len_move_prod': fields.function(
            _check_len_move_prod,
            string='produced', type='integer',),
        'moves_lines2': fields.function(
            _check_move_lines2,
            string='moves_lines2', type='integer',),
    }

    def action_finished_consume(self, cr, uid, ids, context={}):
        stock_move = self.pool.get('stock.move')
        for production in self.browse(cr, uid, ids, context=context):
            for moves in production.move_lines:
                stock_move.action_cancel(cr, uid, [moves.id], context=context)
        return True

    def action_finish(self, cr, uid, ids, context={}):
        stock_move = self.pool.get('stock.move')
        stock_picking = self.pool.get('stock.picking')
        for production in self.browse(cr, uid, ids, context=context):
            for moves in production.move_created_ids:
                stock_move.action_cancel(cr, uid, [moves.id], context=context)
            try:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(
                    uid, 'mrp.production', production.id,
                    'button_produce_done', cr)
            except:
                pass
        return True
