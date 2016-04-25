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
from openerp.tools.translate import _

import openerp.workflow as workflow
#~ from DateTime import DateTime


class AccountMoveCancel(osv.TransientModel):

    _name = 'account.move.cancel'
    _columns = {
        'invoice_ids': fields.many2many('account.invoice', 'invoice_rel',
                                        'invoice1', 'invoice2', 'Invoices',
                                        help="Select the invoices to account move cancel"),

    }

    def cancel_account_move(self, cr, uid, ids, context=None,
                            invoice_ids=False):
        """Cancel invoices to delete account move
            @param invoice_ids, ids list of invoices to method apply
            @param ids, ids of wizard if called from this
        """
        if context is None:
            context = {}
        invo_obj = self.pool.get('account.invoice')

        journal_obj = self.pool.get('account.journal')
        invo_ids = []
        iva_ids = []
        islr_ids = []
        journal_ids = []
        wf_service = workflow
        print "context", context
        if not invoice_ids:
            invo_brw = self.browse(cr, uid, ids, context=context)
            invo_brw = invo_brw[0].invoice_ids
            for invo in invo_brw:
                invo_ids.append(invo.id)
                hasattr(invo, 'islr_wh_doc_id') and invo.islr_wh_doc_id and\
                    islr_ids.append(invo.islr_wh_doc_id.id)
                hasattr(invo, 'wh_iva_id') and invo.wh_iva_id and\
                    iva_ids.append(invo.wh_iva_id.id)
                invo.journal_id and journal_ids.append(invo.journal_id.id)

                hasattr(invo, 'islr_wh_doc_id') and invo.islr_wh_doc_id and\
                    invo.islr_wh_doc_id.journal_id and \
                    journal_ids.append(invo.islr_wh_doc_id.journal_id.id)

                hasattr(invo, 'wh_iva_id') and invo.wh_iva_id and \
                    invo.wh_iva_id.journal_id and \
                    journal_ids.append(invo.wh_iva_id.journal_id.id)

        else:
            invo_brw = invo_obj.browse(cr, uid, invoice_ids, context=context)
            for invo in invo_brw:
                invo_ids.append(invo.id)
                hasattr(invo, 'islr_wh_doc_id') and invo.islr_wh_doc_id and\
                    islr_ids.append(invo.islr_wh_doc_id.id)
                hasattr(invo, 'wh_iva_id') and invo.wh_iva_id and\
                    iva_ids.append(invo.wh_iva_id.id)
                invo.journal_id and journal_ids.append(invo.journal_id.id)

                hasattr(invo, 'islr_wh_doc_id') and invo.islr_wh_doc_id and\
                    invo.islr_wh_doc_id.journal_id and \
                    journal_ids.append(invo.islr_wh_doc_id.journal_id.id)

                hasattr(invo, 'wh_iva_id') and invo.wh_iva_id and\
                    invo.wh_iva_id.journal_id and \
                    journal_ids.append(invo.wh_iva_id.journal_id.id)

        hasattr(journal_obj.browse(cr, uid, journal_ids[0], context=context),
                'update_posted') and \
            journal_obj.write(cr, uid, journal_ids, {
                              'update_posted': True}, context=context)
        if invo_ids:
            if iva_ids and context.get('iva'):
                [cr.execute(
                    "update wkf_instance set state='active' where res_id =%s" %
                    i) for i in iva_ids]

                len(iva_ids) == 1 and wf_service.trg_validate(uid,
                                                              'account.wh.iva', iva_ids[0], 'cancel', cr) or \
                    [wf_service.trg_validate(
                     uid, 'account.wh.iva', i, 'cancel', cr) for i in iva_ids]

            if islr_ids and context.get('islr'):

                [cr.execute(
                    "update wkf_instance set state='active' where res_id =%s" %
                    i) for i in islr_ids]

                len(islr_ids) == 1 and wf_service.trg_validate(uid,
                                                               'islr.wh.doc', islr_ids[0], 'act_cancel', cr) or \
                    [wf_service.trg_validate(
                        uid, 'islr.wh.doc', i, 'act_cancel', cr)
                        for i in islr_ids]

            names = [invo.nro_ctrl for invo in invo_brw if invo.payment_ids]

            if names:
                raise osv.except_osv(_('Invalid action !'), _(
                    "Impossible invoice(s) cancel %s  because is/are paid!"
                    % (' '.join(names))))
            # correccion estaba llegando tupla () al unlink
            invo_obj.action_cancel(cr, uid, invo_ids, context=context)
            invo_obj.write(cr, uid, invo_ids, {
                           'cancel_true': True}, context=context)
            hasattr(journal_obj.browse(cr, uid, journal_ids[0],
                                       context=context), 'update_posted') and \
                journal_obj.write(cr, uid, journal_ids, {
                                  'update_posted': False}, context=context)

        return True

    # nombre del modulo account_anglo_saxon_cost_structure

#~ acttion_cancel asiento (acount_move)
#~ action_move_create (account_invoice)
