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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import pooler, tools
from openerp import netsvc
import time


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def action_cancel(self, cr, uid, ids, context=None):
        ir_attach_facturae_mx_obj = self.pool.get('ir.attachment.facturae.mx')
        inv_type_facturae = {
            'out_invoice': True,
            'out_refund': True,
            'in_invoice': False,
            'in_refund': False}
        for inv in self.browse(cr, uid, ids, context=context):
            if inv_type_facturae.get(inv.type, False):
                ir_attach_facturae_mx_ids = ir_attach_facturae_mx_obj.search(
                    cr, uid, [('invoice_id', '=', inv.id)], context=context)
                for attach in ir_attach_obj.browse(cr, uid, ir_attach_facturae_mx_ids, context=context):
                    if attach.state <> 'cancel':
                        ir_attach_obj.signal_cancel(cr, uid, [attach.id], context=context)
        res = super(account_invoice, self).action_cancel(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'date_invoice_cancel': time.strftime('%Y-%m-%d %H:%M:%S')})
        return res

    def create_ir_attachment_facturae(self, cr, uid, ids, context=None):
        attach = ''
        ir_attach_obj = self.pool.get('ir.attachment.facturae.mx')
        ir_model_data_obj = self.pool.get('ir.model.data')
        attach_ids = []
        inv_type_facturae = {
            'out_invoice': True,
            'out_refund': True,
            'in_invoice': False,
            'in_refund': False}
        for inv in self.browse(cr, uid, ids, context=context):
            if inv_type_facturae.get(inv.type, False):
                approval_id = invoice.invoice_sequence_id and invoice.invoice_sequence_id.approval_id or False
                if approval_id:
                    attach_ids.append( ir_attach_obj.create(cr, uid, {
                      'name': invoice.fname_invoice, 'invoice_id': inv.id,
                      'type': invoice.invoice_sequence_id.approval_id.type},
                      context={})
                    )
        form_res = ir_model_data_obj.get_object_reference(
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
            'res_id': attach_ids,
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'type': 'ir.actions.act_window',
        }
        return True
