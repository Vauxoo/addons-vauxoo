#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Humberto Arocha / Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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

from openerp.osv import osv, fields


class account_move_line(osv.Model):
    _inherit = "account.move.line"

    def _remove_move_reconcile(self, cr, uid, move_ids=[], context=None):
        # Function remove move rencocile ids related with moves
        if context is None:
            context = {}
        obj_move_line = self.pool.get('account.move.line')
        obj_move_rec = self.pool.get('account.move.reconcile')
        unlink_ids = []
        if not move_ids:
            return True
        recs = obj_move_line.read(cr, uid, move_ids, [
                                  'reconcile_id', 'reconcile_partial_id'])
        full_recs = filter(lambda x: x['reconcile_id'], recs)
        rec_ids = [rec['reconcile_id'][0] for rec in full_recs]
        part_recs = filter(lambda x: x['reconcile_partial_id'], recs)
        part_rec_ids = [rec['reconcile_partial_id'][0] for rec in part_recs]

        for rec_brw in obj_move_rec.browse(cr, uid, rec_ids, context=context):
            aml_ids = list(set([rec_line.id for rec_line in rec_brw.line_id]) -
                           set(move_ids))
            obj_move_rec.unlink(cr, uid, [rec_brw.id])
            if len(aml_ids) >= 2:
                obj_move_line.reconcile_partial(
                    cr, uid, aml_ids, 'auto', context=context)

        for part_rec_brw in obj_move_rec.browse(cr, uid, part_rec_ids,
                                                context=context):
            aml_ids = list(set([rec_line.id
                            for rec_line in part_rec_brw.line_partial_ids]) -
                           set(move_ids))
            obj_move_rec.unlink(cr, uid, [part_rec_brw.id])
            if len(aml_ids) >= 2:
                obj_move_line.reconcile_partial(
                    cr, uid, aml_ids, 'auto', context=context)
        return True
