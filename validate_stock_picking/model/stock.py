# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
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
##########################################################################

import time

from openerp.osv import osv
from openerp import workflow
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class InheritStockMove(osv.Model):

    _inherit = 'stock.move'

    def action_done(self, cr, uid, ids, context=None):
        """ Makes the move done and if all moves are done, it will finish the picking.
        @return:
        """
        picking_ids = []
        move_ids = []
        wf_service = workflow
        if context is None:
            context = {}

        todo = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.state == "draft":
                todo.append(move.id)
        if todo:
            self.action_confirm(cr, uid, todo, context=context)
            todo = []

        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ['done', 'cancel']:
                continue
            move_ids.append(move.id)

            if move.picking_id:
                picking_ids.append(move.picking_id.id)
            if move.move_dest_id.id and (move.state != 'done'):
                # Downstream move should only be triggered if this move is the
                # last pending upstream move
                other_upstream_move_ids = self.search(
                    cr,
                    uid,
                    [('id', '!=', move.id),
                     ('state', 'not in', ['done', 'cancel']),
                     ('move_dest_id', '=', move.move_dest_id.id)],
                    context=context)
                if not other_upstream_move_ids:
                    self.write(
                        cr,
                        uid,
                        [move.id],
                        {'move_history_ids': [(4, move.move_dest_id.id)]})
                    if move.move_dest_id.state in ('waiting', 'confirmed'):
                        self.force_assign(
                            cr, uid, [move.move_dest_id.id], context=context)
                        if move.move_dest_id.picking_id:
                            wf_service.trg_write(
                                uid,
                                'stock.picking',
                                move.move_dest_id.picking_id.id,
                                cr)
                        if move.move_dest_id.auto_validate:
                            self.action_done(
                                cr,
                                uid,
                                [move.move_dest_id.id],
                                context=context)

            self._create_product_valuation_moves(
                cr, uid, move, context=context)
            if move.state not in ('confirmed', 'done', 'assigned'):
                todo.append(move.id)

        if todo:
            self.action_confirm(cr, uid, todo, context=context)

        if context.get('no_change_date', False):
            self.write(cr, uid, move_ids, {'state': 'done'}, context=context)
        else:
            self.write(
                cr,
                uid,
                move_ids,
                {'state': 'done',
                 'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)},
                context=context)

        for id in move_ids:
            wf_service.trg_trigger(uid, 'stock.move', id, cr)

        for pick_id in picking_ids:
            wf_service.trg_write(uid, 'stock.picking', pick_id, cr)

        return True
