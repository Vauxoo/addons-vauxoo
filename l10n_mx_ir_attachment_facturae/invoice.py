#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# Credits######################################################
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
##########################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools
from openerp import netsvc
import time


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def action_cancel(self, cr, uid, ids, context=None):
        ir_attach_obj = self.pool.get('ir.attachment.facturae.mx')
        id_attach = ir_attach_obj.search(
            cr, uid, [('invoice_id', '=', ids[0])], context={})
        wf_service = netsvc.LocalService("workflow")
        inv_type_facturae = {
            'out_invoice': True,
            'out_refund': True,
            'in_invoice': False,
            'in_refund': False}
        for inv in self.browse(cr, uid, ids):
            if inv_type_facturae.get(inv.type, False):
                if id_attach:
                    for attach in ir_attach_obj.browse(cr, uid, id_attach):
                        if attach.state=='cancel':
                            self.write(cr, uid, ids, {'date_invoice_cancel': time.strftime('%Y-%m-%d %H:%M:%S')})
                            return super(account_invoice,
                                 self).action_cancel(cr, uid, ids, context)
                        else:
                            self.pool.get('ir.attachment.facturae.mx').signal_cancel(cr, uid, id_attach, context=None)
                            return super(account_invoice,
                                 self).action_cancel(cr, uid, ids, context)

    def create_ir_attachment_facturae(self, cr, uid, ids, context=None):
        try:
            attach = ''
            ir_attach_obj = self.pool.get('ir.attachment.facturae.mx')
            invoice = self.browse(cr, uid, ids, context={})[0]
            inv_type_facturae = {
                'out_invoice': True,
                'out_refund': True,
                'in_invoice': False,
                'in_refund': False}
            for inv in self.browse(cr, uid, ids):
                if inv_type_facturae.get(inv.type, False):
                    if invoice._columns.has_key('invoice_sequence_id') and invoice.invoice_sequence_id and invoice.invoice_sequence_id.approval_id:
                        if invoice.invoice_sequence_id and invoice.invoice_sequence_id.approval_id and invoice.invoice_sequence_id.approval_id.type:
                            attach = ir_attach_obj.create(cr, uid, {
                                                              'name': invoice.fname_invoice, 'invoice_id': ids[0],
                                                              'type': invoice.invoice_sequence_id.approval_id.type},
                                                              context={})
                            ir_model_data = self.pool.get('ir.model.data')
                            form_res = ir_model_data.get_object_reference(
                                cr, uid, 'l10n_mx_ir_attachment_facturae',
                                'view_ir_attachment_facturae_mx_form')
                            form_id = form_res and form_res[1] or False

                            tree_res = ir_model_data.get_object_reference(
                                cr, uid, 'l10n_mx_ir_attachment_facturae',
                                'view_ir_attachment_facturae_mx_tree')
                            tree_id = tree_res and tree_res[1] or False

                            return {
                                'name': _('Attachment Factura E MX'),
                                'view_type': 'form',
                                'view_mode': 'form,tree',
                                'res_model': 'ir.attachment.facturae.mx',
                                'res_id': attach,
                                'view_id': False,
                                'views': [(form_id, 'form'), (tree_id, 'tree')],
                                'type': 'ir.actions.act_window',
                            }
                        else:
                            raise osv.except_osv(_('Warning'), _('No exists type of electroncic invoice'))
                    else:
                        raise osv.except_osv(_('Warning'), _('No valid approval of folios'))
            return True
        except:
            return False
