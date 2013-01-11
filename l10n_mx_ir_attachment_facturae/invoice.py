#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Juan Carlos Funes(juan@vauxoo.com)
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
################################################################################

from osv import fields, osv, orm
from tools.translate import _
import netsvc
import time

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def action_cancel(self, cr, uid, ids, context, *args):
        id_attach=self.pool.get('ir.attachment.facturae.mx').search(cr, uid, [('invoice_id','=',ids[0])])
        wf_service = netsvc.LocalService("workflow")
        inv_type_facturae = {'out_invoice': True, 'out_refund': True, 'in_invoice': False, 'in_refund': False}
        for inv in self.browse(cr, uid, ids):
            if inv_type_facturae.get(inv.type, False):
                for attachment in self.pool.get('ir.attachment.facturae.mx').browse(cr, uid, id_attach, context):
                    if attachment.state=='done':
                        wf_service.trg_validate(uid, 'ir.attachment.facturae.mx', attachment.id, 'action_cancel', cr)
        self.write(cr, uid, ids, {'date_invoice_cancel': time.strftime('%Y-%m-%d %H:%M:%S')})
        return super(account_invoice, self).action_cancel(cr, uid, ids, args)

    def action_number(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        res=super(account_invoice, self).action_number(cr, uid, ids, context)
        invoice = self.browse(cr, uid, ids, context=context)[0]
        id_attach=self.pool.get('ir.attachment.facturae.mx').search(cr, uid, [('invoice_id','=',ids[0])])
        for attachment in self.pool.get('ir.attachment.facturae.mx').browse(cr, uid, id_attach, context):
            continue
        if not id_attach or attachment.state in ('cancel'):
            attach=self.pool.get('ir.attachment.facturae.mx').create(cr, uid, {
            'name': invoice.number,
            'invoice_id': ids[0],
            'type': invoice.invoice_sequence_id.approval_id.type }, context=context)
            wf_service.trg_validate(uid, 'ir.attachment.facturae.mx', attach, 'action_confirm', cr)
            wf_service.trg_validate(uid, 'ir.attachment.facturae.mx', attach, 'action_sign', cr)
            wf_service.trg_validate(uid, 'ir.attachment.facturae.mx', attach, 'action_printable', cr)
            wf_service.trg_validate(uid, 'ir.attachment.facturae.mx', attach, 'action_send_backup', cr)
            wf_service.trg_validate(uid, 'ir.attachment.facturae.mx', attach, 'action_send_customer', cr)
            wf_service.trg_validate(uid, 'ir.attachment.facturae.mx', attach, 'action_done', cr)
        return res

account_invoice()
