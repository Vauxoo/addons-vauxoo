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
        if context is None:
            context = {}
        res = False
        ids = isinstance(ids, (int, long)) and [ids] or ids
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
                if ir_attach_facturae_mx_ids:
                    for attach in ir_attach_facturae_mx_obj.browse(cr, uid, ir_attach_facturae_mx_ids, context=context):
                        if attach.state <> 'cancel':
                            res = super(account_invoice, self).action_cancel(cr, uid, ids, context=context)
                            if res:
                                attach = ir_attach_facturae_mx_obj.signal_cancel(cr, uid, [attach.id], context=context)
                                if attach:
                                    self.write(cr, uid, ids, {'date_invoice_cancel': time.strftime('%Y-%m-%d %H:%M:%S')})
                else:
                    res = super(account_invoice, self).action_cancel(cr, uid, ids, context=context)
        return res

    def create_ir_attachment_facturae(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        attach = ''
        ir_attach_obj = self.pool.get('ir.attachment.facturae.mx')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        attach_ids = []
        inv_type_facturae = {
            'out_invoice': True,
            'out_refund': True,
            'in_invoice': False,
            'in_refund': False}
        file_globals = self._get_file_globals(cr, uid, ids, context=context)
        fname_cer_no_pem = file_globals['fname_cer']
        cerCSD = open(fname_cer_no_pem).read().encode('base64') #Mejor forma de hacerlo
        fname_key_no_pem = file_globals['fname_key']
        keyCSD = fname_key_no_pem and base64.encodestring(open(fname_key_no_pem, "r").read()) or ''
        for invoice in self.browse(cr, uid, ids, context=context):
            if inv_type_facturae.get(invoice.type, False):
                approval_id = invoice.invoice_sequence_id and invoice.invoice_sequence_id.approval_id or False
                if approval_id:
                    xml_fname, xml_data = obj_source._get_facturae_invoice_xml_data(
                            cr, uid, ids, context=context)
                    attach_ids.append( ir_attach_obj.create(cr, uid, {
                        'name': invoice.fname_invoice, 
                        'type': invoice.invoice_sequence_id.approval_id.type,
                        'journal_id': invoice.journal_id and invoice.journal_id.id or False,
                        'company_emitter_id': invoice.company_emitter_id.id,
                        'model_source': self._name or '',
                        'id_source': invoice.id,
                        'attachment_email': invoice.partner_id.email or '',
                        'certificate_password': file_globals.get('password', ''),
                        'certificate_file': cerCSD or '',
                        'certificate_key_file': keyCSD or '',
                        'user_pac': '',
                        'password_pac': '',
                        'url_webservice_pac': '',
                        'file_input_index': xml_data or '',
                        },
                      context=context)#Context, because use a variable type of our code but we dont need it.
                    )
                    ir_attach_obj.signal_confirm(cr, uid, attach_ids, context=context)
        if attach_ids:
            result = mod_obj.get_object_reference(cr, uid, 'l10n_mx_ir_attachment_facturae',
                                                            'action_ir_attachment_facturae_mx')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            #choose the view_mode accordingly
            result['domain'] = "[('id','in',["+','.join(map(str, attach_ids))+"])]"
            result['res_id'] = attach_ids and attach_ids[0] or False
            res = mod_obj.get_object_reference(cr, uid, 'l10n_mx_ir_attachment_facturae', 
                                                            'view_ir_attachment_facturae_mx_form')
            result['views'] = [(res and res[1] or False, 'form')]
            return result
        return True
