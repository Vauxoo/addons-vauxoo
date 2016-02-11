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

from openerp.osv import osv
from openerp.tools.translate import _

import openerp.workflow as workflow


class AccountInvoice(osv.Model):

    _inherit = 'account.invoice'

# ~ def action_cancel_draft(self, cr, uid, ids, *args):
# ~
    # ~ wf_service = workflow
    # ~ res = super(account_invoice, self).action_cancel_draft(
    # ~     cr, uid, ids, ())
    # ~ for i in self.browse(cr,uid,ids,context={}):
    # ~ if i.wh_iva_id:
    # ~ wf_service.trg_validate(uid, 'account.wh.iva',i.wh_iva_id.id,
    # ~                         'set_to_draft', cr)
    # ~ return res
    def action_number(self, cr, uid, ids, context=None):
        '''
        Modified to witholding vat validate
        '''
        wf_service = workflow
        res = super(AccountInvoice, self).action_number(cr, uid, ids)
        iva_line_obj = self.pool.get('account.wh.iva.line')
        invo_brw = self.browse(cr, uid, ids, context=context)[0]
        state = [('draft', 'set_to_draft'), (
            'confirmed', 'wh_iva_confirmed'), ('done', 'wh_iva_done')]
        if invo_brw.cancel_true:
            if invo_brw.wh_iva_id:
                iva_line_obj.load_taxes(cr, uid, [
                    i.id for i in invo_brw.wh_iva_id.wh_lines],
                    context=context)
                for d in state:
                    if invo_brw.wh_iva_id.prev_state == 'cancel':
                        break

                    if not all([False for line in invo_brw.wh_iva_id.wh_lines
                                if not line.invoice_id.move_id]):
                        raise osv.except_osv(_('Error'), _(
                            'One of the bills involved in the vat retention\
                                has not been validated, because it does not\
                                have an associated retention'))
                    wf_service.trg_validate(
                        uid, 'account.wh.iva', invo_brw.wh_iva_id.id, d[1], cr)

                    if d[0] == invo_brw.wh_iva_id.prev_state:
                        break

        return res

    def invoice_cancel(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        context.update({'iva': True})
        iva_obj = self.pool.get('account.wh.iva')
        invo_brw = self.browse(cr, uid, ids, context=context)[0]
        if invo_brw.wh_iva_id:
            iva_obj.write(cr, uid, [invo_brw.wh_iva_id.id], {
                'prev_state': invo_brw.wh_iva_id.state},
                context=context)

        res = super(AccountInvoice, self).invoice_cancel(
            cr, uid, ids, context=context)

        return res

    def check_iva(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invo_brw = self.browse(cr, uid, ids[0], context=context)
        if invo_brw.wh_iva_id:
            return False
        return True
