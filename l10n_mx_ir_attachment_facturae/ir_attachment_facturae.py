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
from openerp import release

import time
import tempfile
import base64
import os


class ir_attachment_facturae_mx(osv.Model):
    _name = 'ir.attachment.facturae.mx'
    _inherit = ['mail.thread', 'ir.needaction_mixin']


    def _get_type(self, cr, uid, ids=None, context=None):
        types = []
        return types
        
    _columns = {
        'name': fields.char('Name', size=128, required=True, readonly=True,
            help='Name of attachment generated'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice',
            readonly=True, help='Invoice to which it belongs this attachment'),
        'company_id': fields.many2one('res.company', 'Company', readonly=True,
            help='Company to which it belongs this attachment'),
        'file_input': fields.many2one('ir.attachment', 'File input',
            readonly=True, help='File input'),
        'file_input_index': fields.text('File input',
            help='File input index'),
        'file_xml_sign': fields.many2one('ir.attachment', 'File XML Sign',
            readonly=True, help='File XML signed'),
        'file_xml_sign_index': fields.text('File XML Sign Index',
            help='File XML sign index'),
        'file_pdf': fields.many2one('ir.attachment', 'File PDF', readonly=True,
            help='Report PDF generated for the electronic Invoice'),
        'file_pdf_index': fields.text('File PDF Index',
            help='Report PDF with index'),
        'identifier': fields.char('Identifier', size=128, ),
        'type': fields.selection(_get_type, 'Type', type='char', size=64,
            readonly=True, help="Type of Electronic Invoice"),
        'description': fields.text('Description'),
        'msj': fields.text('Last Message', readonly=True,
            track_visibility='onchange',
            help='Message generated to upload XML to sign'),
        'last_date': fields.datetime('Last Modified', readonly=True,
            help='Date when is generated the attachment'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('signed', 'Signed'),
            ('printable', 'Printable Format Generated'),
            ('sent_customer', 'Sent Customer'),
            ('sent_backup', 'Sent Backup'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),],
            'State', readonly=True, required=True, help='State of attachments'),
    }

    _defaults = {
        'state': 'draft',
        'company_id': lambda self, cr, uid, c:
        self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        'last_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    def action_create_ir_attachment_facturae(self, cr, uid, ids, context=None):
        ir_attachment_fact = self.browse(cr, uid, ids, context=context)[0]
        attach = ir_attachment_fact.id
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(
            uid, 'ir.attachment.facturae.mx', attach, 'action_sign', cr)
        #TODO: Remplazar los commit y los traceback por un mail.message
        #cr.commit()
        wf_service.trg_validate(
            uid, 'ir.attachment.facturae.mx', attach, 'action_printable', cr)
        #cr.commit()
        wf_service.trg_validate(
            uid, 'ir.attachment.facturae.mx', attach, 'action_send_backup', cr)
        #cr.commit()
        wf_service.trg_validate(
            uid, 'ir.attachment.facturae.mx', attach, 'action_send_customer', cr)
        #cr.commit()
        wf_service.trg_validate(
            uid, 'ir.attachment.facturae.mx', attach, 'action_done', cr)
        #cr.commit()

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

    def action_confirm(self, cr, uid, ids, context=None):
        attach = ''
        invoice = self.browse(cr, uid, ids)[0].invoice_id
        invoice_obj = self.pool.get('account.invoice')
        type = self.browse(cr, uid, ids)[0].type
        if type == 'cfd22':
            fname_invoice = invoice.fname_invoice and invoice.fname_invoice + \
                '.xml' or ''
            fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(
                cr, uid, [invoice.id], context=context)
            attach = self.pool.get('ir.attachment').create(cr, uid, {
                'name': fname_invoice,
                'datas': base64.encodestring(xml_data),
                'datas_fname': fname_invoice,
                'res_model': 'account.invoice',
                'res_id': invoice.id,
            }, context=context)
            if not attach:
                msj = "Error XML CFD 2.2\n"
        if type == 'cfdi32':
            fname_invoice = invoice.fname_invoice and invoice.fname_invoice + \
                '_V2_2.xml' or ''
            fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(
                cr, uid, [invoice.id], context=context)
            attach = self.pool.get('ir.attachment').create(cr, uid, {
                'name': fname_invoice,
                'datas': base64.encodestring(xml_data),
                'datas_fname': fname_invoice,
                'res_model': 'account.invoice',
                #'res_id': invoice.id,
            }, context=context)
            if not attach:
                msj = _("Not Applicable XML CFD 2.2\n")
        if attach:
            msj = _("Attached Successfully XML CFD 2.2\n")
        else:
            msj = _("Not Applicable XML CFD 2.2\n")
        return self.write(cr, uid, ids,
                          {'state': 'confirmed',
                           'file_input': attach or False,
                           'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                           'msj': msj}, context=context)

    def action_sign(self, cr, uid, ids, context={}):
        attach = ''
        res = {'msg': ''}
        invoice = self.browse(cr, uid, ids)[0].invoice_id
        msj = self.browse(cr, uid, ids)[0].msj
        invoice_obj = self.pool.get('account.invoice')
        attachment_obj = self.pool.get('ir.attachment')
        type = self.browse(cr, uid, ids)[0].type
        if type == 'cfd22':
            aids = self.browse(cr, uid, ids)[0].file_input or False
        if type == 'cfdi32':
            fname_invoice = invoice.fname_invoice and invoice.fname_invoice + \
                '.xml' or ''
            fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(
                cr, uid, [invoice.id], context=context)
            fdata = base64.encodestring(xml_data)
            res = invoice_obj._upload_ws_file(
                cr, uid, [invoice.id], fdata, context={})
            msj = tools.ustr(res['msg']) + '\n'
            if res['status'] == '500':
                raise osv.except_osv(_('Warning'), _(res['msg']))
            if res['status'] == '301':
                raise osv.except_osv(_('Warning'), _(res['msg']))
            data_attach = {
                'name': fname_invoice,
                'datas': base64.encodestring(res['cfdi_xml'] or '') or False,
                'datas_fname': fname_invoice,
                'description': 'Factura-E XML CFD-I SIGN',
                'res_model': 'account.invoice',
                'res_id': invoice.id,
            }
            attach = attachment_obj.create(
                cr, uid, data_attach, context=context)
        return self.write(cr, uid, ids,
                          {'state': 'signed',
                           'file_xml_sign': attach,
                           'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                           'msj': msj}, context=context)

    def action_printable(self, cr, uid, ids, context={}):
        aids = []
        invoice = self.browse(cr, uid, ids)[0].invoice_id
        msj = self.browse(cr, uid, ids)[0].msj
        invoice_obj = self.pool.get('account.invoice')
        type = self.browse(cr, uid, ids)[0].type
        (fileno, fname) = tempfile.mkstemp(
            '.pdf', 'openerp_' + (False or '') + '__facturae__')
        os.close(fileno)
        freport = invoice_obj.create_report(cr, uid, [invoice.id],
            "account.invoice.facturae.webkit", fname)
        #file = invoice_obj.create_report(cr, uid, [invoice.id],
            #"account.invoice", fname)
        attachment_ids = self.pool.get('ir.attachment').search(cr, uid,
            [('res_model', '=', 'account.invoice'), ('res_id', '=', invoice.id),
            ('datas_fname', '=', invoice.fname_invoice+'.pdf')])
        for attachment in self.browse(cr, uid, attachment_ids, context=context):
            aids = attachment.id #TODO: aids.append( attachment.id ) but without error in last write
            self.pool.get('ir.attachment').write(cr, uid, [attachment.id], {
                'name': invoice.fname_invoice + '.pdf', }, context={})
        if aids:
            msj = _("Attached Successfully PDF\n")
        else:
            msj = _("Not Attached PDF\n")
        writed = self.write(cr, uid, ids, {
            'state': 'printable',
            'file_pdf': aids or False,
            'msj': msj,
            'last_date': time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        return writed

    def action_send_customer(self, cr, uid, ids, context=None):
        attachments = []
        msj = ''
        attach_name = ''
        state = ''
        invoice = self.browse(cr, uid, ids)[0].invoice_id
        address_id = self.pool.get('res.partner').address_get(
            cr, uid, [invoice.partner_id.id], ['invoice'])['invoice']
        partner_invoice_address = self.pool.get(
            'res.partner').browse(cr, uid, address_id, context)
        type = self.browse(cr, uid, ids)[0].type
        msj = self.browse(cr, uid, ids)[0].msj
        fname_invoice = invoice.fname_invoice and invoice.fname_invoice or ''
        adjuntos = self.pool.get('ir.attachment').search(cr, uid, [(
            'res_model', '=', 'account.invoice'), ('res_id', '=', invoice)])
        subject = 'Invoice '+invoice.number or False
        for attach in self.pool.get('ir.attachment').browse(cr, uid, adjuntos):
            attachments.append(attach.id)
            attach_name += attach.name + ', '
        if release.version >= '7':
            mail_compose_message_pool = self.pool.get('mail.compose.message')
            tmp_id = self.get_tmpl_email_id(cr, uid, ids, context=context)
            message = mail_compose_message_pool.onchange_template_id(
                cr, uid, [], template_id=tmp_id, composition_mode=None,
                model='account.invoice', res_id=invoice.id, context=context)
            mssg = message.get('value', False)
            if mssg.get('partner_ids', False) and tmp_id:
                mssg['partner_ids'] = [(6, 0, mssg['partner_ids'])]
                mssg['attachment_ids'] = [(6, 0, attachments)]
                mssg_id = self.pool.get(
                    'mail.compose.message').create(cr, uid, mssg)
                state = self.pool.get('mail.compose.message').send_mail(
                    cr, uid, [mssg_id], context=context)
                msj = _('Email Send Successfully\n')
            else:
                msj = _('Not Email Send\n')
        elif release.version < '7':
            mail = self.pool.get('mail.message').create(cr, uid, {
                'subject': subject+' '+type,
                'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'email_from': email_from,
                'email_to': invoice.address_invoice_id.email,
                'auto_delete': False,
                'body_text': attach_name,
                'attachment_ids': [(6, 0, attachments)],
                'model': invoice._name,
                'res_id': invoice.id,
            }, context=context)
            state = self.pool.get('mail.message').send(
                cr, uid, [mail], auto_commit=False, context=context)
        # if not state:
            # msj +=_('Please Check the Email Configuration!\n')
        # else:
            # msj +=_('Email Send Successfully\n')
        return self.write(cr, uid, ids, {'state': 'sent_customer', 'msj': msj,
            'last_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    def action_send_backup(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'sent_backup'})

    def action_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'})

    def action_cancel(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        attach_obj = self.pool.get('ir.attachment')
        type = self.browse(cr, uid, ids)[0].type
        invoice = self.browse(cr, uid, ids)[0].invoice_id
        msj = self.browse(cr, uid, ids)[0].msj
        if type == 'cfdi32':
            get_file_cancel = invoice_obj._get_file_cancel(
                cr, uid, [invoice], context={})
            sf_cancel = invoice_obj.sf_cancel(
                cr, uid, [invoice.id], context={})
            msj = tools.ustr(sf_cancel['message'])
        adjuntos = self.pool.get('ir.attachment').search(cr, uid, [(
            'res_model', '=', 'account.invoice'), ('res_id', '=', invoice)])
        for attachment in self.browse(cr, uid, adjuntos, context):
            ids2 = attach_obj.write(cr, uid, [attachment.id], {
                                    'res_id': False, }, context={})
        return self.write(cr, uid, ids,
                          {'state': 'cancel',
                           'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                           'msj': msj, })

    def reset_to_draft(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for row in self.browse(cr, uid, ids, context=context):
            # Deleting the existing instance of workflow
            wf_service.trg_delete(uid, 'ir.attachment.facturae.mx', row.id, cr)
            wf_service.trg_create(uid, 'ir.attachment.facturae.mx', row.id, cr)
        return self.write(cr, uid, ids, {'state': 'draft'})

    def get_tmpl_email_id(self, cr, uid, ids, context=None):
        email_pool = self.pool.get('email.template')
        email_ids = email_pool.search(cr, uid, [(
            'model_id.model', '=', 'account.invoice')])
        return email_ids and email_ids[0] or False
        
class ir_attachment(osv.Model):
    _inherit = 'ir.attachment'
    
    def unlink(self, cr, uid, ids, context=None):
        attachments = self.pool.get('ir.attachment.facturae.mx').search(cr, uid, ['|', '|', ('file_input', 'in', ids), ('file_xml_sign', 'in', ids), ('file_pdf', 'in', ids)])
        if attachments:
            raise osv.except_osv(_('Warning!'), _('You can not remove an attachment of an invoice'))
        return super(ir_attachment, self).unlink(cr, uid, ids, context=context)
    
