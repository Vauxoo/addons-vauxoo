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

from openerp.osv import osv


class account_move_line(osv.Model):
    _inherit = "account.move.line"

    def _remove_move_reconcile(self, cr, uid, move_ids=None,
                               opening_reconciliation=False, context=None):
        # Function remove move reconcile ids related with moves
        if opening_reconciliation:
            # We will return original method
            super(account_move_line, self)._remove_move_reconcile(
                cr, uid, move_ids=move_ids,
                opening_reconciliation=opening_reconciliation, context=context)
        context = dict(context or {})
        aml_obj = self.pool.get('account.move.line')
        amr_obj = self.pool.get('account.move.reconcile')
        if not move_ids:
            return True
        aml_brws = aml_obj.browse(cr, uid, move_ids, context=context)
        rec_dict = {}
        for aml_brw in aml_brws:
            rec_id = aml_brw.reconcile_id or aml_brw.reconcile_partial_id
            # We will not unreconcile something that is not reconciled
            if not rec_id:
                continue
            if rec_id.id not in rec_dict.keys():
                rec_dict[rec_id.id] = set([aml_brw.id])
            else:
                rec_dict[rec_id.id].add(aml_brw.id)

        for amr_brw in amr_obj.browse(cr, uid, rec_dict.keys(),
                                      context=context):
            full_ids = [fbrw.id for fbrw in amr_brw.line_id]
            part_ids = [pbrw.id for pbrw in amr_brw.line_partial_ids]
            aml_ids = set(full_ids + part_ids) - rec_dict[amr_brw.id]
            amr_brw.unlink()
            if len(aml_ids) > 1:
                aml_obj.reconcile_partial(cr, uid, list(aml_ids),
                                          'auto', context=context)
        return True
