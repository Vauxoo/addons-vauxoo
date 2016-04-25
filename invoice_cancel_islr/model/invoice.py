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

from openerp.osv import osv

import openerp.workflow as workflow


class AccountInvoice(osv.Model):
    _inherit = 'account.invoice'

    #~
    #~ def action_cancel_draft(self, cr, uid, ids, *args):
    #~
    #~ wf_service = workflow
    #~ res = super(account_invoice, self).action_cancel_draft(cr, uid, ids, ())
    #~ for i in self.browse(cr,uid,ids,context={}):
    #~ if i.islr_wh_doc_id:
    #~ wf_service.trg_validate(uid, 'islr.wh.doc',i.islr_wh_doc_id.id, 'act_draft', cr)
    #~ return res

    def action_number(self, cr, uid, ids, context=None):
        """Modified to witholding vat validate
        """
        wf_service = workflow
        res = super(AccountInvoice, self).action_number(cr, uid, ids)
        invo_brw = self.browse(cr, uid, ids, context=context)[0]
        state = [('draft', 'act_draft'), ('progress', 'act_progress'), (
            'confirmed', 'act_confirmed'), ('done', 'act_done')]
        if invo_brw.cancel_true:
            if invo_brw.islr_wh_doc_id:
                for i in state:

                    if invo_brw.islr_wh_doc_id.prev_state == 'cancel':
                        break

                    wf_service.trg_validate(
                        uid, 'islr.wh.doc', invo_brw.islr_wh_doc_id.id, i[1],
                        cr)

                    if i[0] == invo_brw.islr_wh_doc_id.prev_state:
                        break

        return res

    def invoice_cancel(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        islr_obj = self.pool.get('islr.wh.doc')
        context.update({'islr': True})
        invo_brw = self.browse(cr, uid, ids, context=context)[0]
        if invo_brw.islr_wh_doc_id:
            islr_obj.write(cr, uid, [invo_brw.islr_wh_doc_id.id], {
                           'prev_state': invo_brw.islr_wh_doc_id.state},
                           context=context)
        res = super(AccountInvoice, self).invoice_cancel(
            cr, uid, ids, context=context)

        return res

    def check_islr(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invo_brw = self.browse(cr, uid, ids[0], context=context)
        if invo_brw.islr_wh_doc_id:
            return False
        return True
