# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
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

from openerp.osv import osv
import time


class AccountMoveLineReconcileWriteoff(osv.osv_memory):

    _inherit = 'account.move.line.reconcile.writeoff'

    def trans_rec_reconcile_partial(self, cr, uid, ids, context=None):
        """This function is overwrite because we need reconcile also
            the aml of taxes when is reconcile partial """
        if context is None:
            context = {}
        res = super(
            AccountMoveLineReconcileWriteoff,
            self).trans_rec_reconcile_partial(cr, uid, ids, context=context)

        self.trans_rec_reconcile_tax(
            cr, uid, context.get('active_ids', []), context=context)

        return res

    def trans_rec_reconcile(self, cr, uid, ids, context=None):
        """This function is overwrite because we need reconcile also
            the aml of taxes and create journal items with difference by
            writeoff in manual reconcile """
        if context is None:
            context = {}

        period_obj = self.pool.get('account.period')
        date = time.strftime('%Y-%m-%d')
        period_id = False

        res = super(
            AccountMoveLineReconcileWriteoff,
            self).trans_rec_reconcile(cr, uid, ids, context=context)

        for writeoff_rec in self.browse(cr, uid, ids, context=context):
            if writeoff_rec.date_p:
                date = writeoff_rec.date_p

            period_ids = period_obj.find(cr, uid, dt=date, context=context)
            if period_ids:
                period_id = period_ids[0]

            self.trans_rec_reconcile_tax(
                cr, uid, context.get('active_ids', []),
                account_id=writeoff_rec.writeoff_acc_id.id,
                period_id=period_id,
                journal_id=writeoff_rec.journal_id.id,
                context=context)

        return res

    def trans_rec_reconcile_tax(
            self, cr, uid, ids, account_id=None, period_id=None,
            journal_id=None, context=None):
        """ This function get ids of aml with account recivable/payable and
            get ids of aml taxes to reconcile in manual process
            writeoff/partial
            param @account_id: to use this account when reconcile is with
                writeoff account is set in wizard
            param @period_id: to use this period when reconcile is writeoff
                this value is calculated
            param @journal_id: to use thi journal_id when reconcile is
                writeoff this value is set in wizard """
        if context is None:
            context = {}
        account_move_line_obj = self.pool.get('account.move.line')
        move_tax_ids = {}
        for move_line in account_move_line_obj.browse(
                cr, uid, ids, context=context):

            for move_line_id in move_line.move_id.line_id:
                if move_line_id.account_id.reconcile and\
                        move_line_id.id not in ids:
                    move_tax_ids.setdefault(
                        move_line_id.account_id.id, []).append(move_line_id.id)

        for move_line_account_reconcile in move_tax_ids:

            if period_id and account_id and journal_id:
                account_move_line_obj.reconcile(
                    cr, uid, move_tax_ids[move_line_account_reconcile],
                    'manual', account_id, period_id, journal_id,
                    context=context)
            else:
                account_move_line_obj.reconcile_partial(
                    cr, uid, move_tax_ids[move_line_account_reconcile],
                    'manual', context=context)
        return True
