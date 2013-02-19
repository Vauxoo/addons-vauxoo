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
from openerp.tools.translate import _
import time
from osv import fields, osv, orm
import tempfile
import base64
import os
import netsvc
import tools
import release

class ir_attachment_facturae_mx(osv.osv):
    _name = 'ir.attachment.facturae.mx'

    def _get_type(self, cr, uid, ids=None, context=None):
        types = []
        return types

    _columns = {
        'name': fields.char('Name', size=128, required=True, readonly=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'file_input': fields.many2one('ir.attachment', 'File input',readonly=True),
        'file_input_index': fields.text('File input'),
        'file_xml_sign': fields.many2one('ir.attachment', 'File XML Sign',readonly=True),
        'file_xml_sign_index': fields.text('File XML Sign Index'),
        'file_pdf': fields.many2one('ir.attachment', 'File PDF',readonly=True),
        'file_pdf_index': fields.text('File PDF Index'),
        'identifier': fields.char('Identifier', size=128),
        'type': fields.selection(_get_type, 'Type', type='char', size=64, readonly=True, help="Type of Electronic Invoice"),
        'description': fields.text('Description'),
        'msj': fields.text('Last Message', readonly=True),
        'last_date': fields.datetime('Last Modified', readonly=True),
        'state': fields.selection([
                ('draft', 'Draft'),
                ('confirmed', 'Confirmed'),
                ('signed', 'Signed'),
                ('printable', 'Printable Format Generated'),
                ('sent_customer', 'Sent Customer'),
                ('sent_backup', 'Sent Backup'),
                ('done', 'Done'),
                ('cancel', 'Cancelled'),
            ], 'State', readonly=True, required=True),
    }

    _defaults = {
        'state': 'draft',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        'last_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    def action_confirm(self, cr, uid, ids, context=None):
        attach=''
        invoice =self.browse(cr,uid,ids)[0].invoice_id
        invoice_obj = self.pool.get('account.invoice')
        type=self.browse(cr,uid,ids)[0].type
        if type=='cfd22':
            fname_invoice = invoice.fname_invoice and invoice.fname_invoice + '.xml' or ''
            fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(cr, uid, [invoice.id] , context=context)
            attach=self.pool.get('ir.attachment').create(cr, uid, {
                'name': fname_invoice,
                'datas': base64.encodestring(xml_data),
                'datas_fname': fname_invoice,
                'res_model': 'account.invoice',
                'res_id': invoice.id,
                }, context=context)
            if not attach:
                msj="Error XML CFD 2.2\n"
        if type=='cfdi32':
            fname_invoice = invoice.fname_invoice and invoice.fname_invoice + '_V2_2.xml' or ''
            fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(cr, uid, [invoice.id] , context=context)
            attach=self.pool.get('ir.attachment').create(cr, uid, {
                'name': fname_invoice,
                'datas': base64.encodestring(xml_data),
                'datas_fname': fname_invoice,
                'res_model': 'account.invoice',
                #'res_id': invoice.id,
                }, context=context)
            if not attach:
                msj="Not Applicable XML CFD 2.2\n"
        if attach:
            msj="Attached Successfully XML CFD 2.2\n"
        else:
            msj="Not Applicable XML CFD 2.2\n"
        return self.write(cr, uid, ids, {'state': 'confirmed', 'file_input': attach or False, 'last_date': time.strftime('%Y-%m-%d %H:%M:%S'), 'msj': msj}, context=context)

    def action_sign(self, cr, uid, ids, context={}):
        attach=''
        res= {'msg':''}
        invoice =self.browse(cr,uid,ids)[0].invoice_id
        msj = self.browse(cr,uid,ids)[0].msj
        invoice_obj = self.pool.get('account.invoice')
        attachment_obj = self.pool.get('ir.attachment')
        type=self.browse(cr,uid,ids)[0].type
        if type=='cfd22':
            aids = self.browse(cr,uid,ids)[0].file_input
            msj += 'Attached Successfully XML CFD 2.2\n'
        if type=='cfdi32':
            fname_invoice = invoice.fname_invoice and invoice.fname_invoice + '.xml' or ''
            fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(cr, uid, [invoice.id] , context=context)
            fdata = base64.encodestring( xml_data )
            res = invoice_obj._upload_ws_file(cr, uid, [invoice.id], fdata, context={})
            msj += tools.ustr(res['msg']) + '\n'
            if res['status']=='500':
                raise osv.except_osv(_('Warning'), _(res['msg']))
            if res['status']=='301':
                raise osv.except_osv(_('Warning'), _(res['msg']))
            data_attach = {
                    'name': fname_invoice,
                    'datas': base64.encodestring( res['cfdi_xml'] or '') or False,
                    'datas_fname': fname_invoice,
                    'description': 'Factura-E XML CFD-I SIGN',
                    'res_model': 'account.invoice',
                    'res_id': invoice.id,
                }
            attach = attachment_obj.create(cr, uid, data_attach, context=context)
        return self.write(cr, uid, ids, {'state': 'signed', 'file_xml_sign': attach, 'last_date': time.strftime('%Y-%m-%d %H:%M:%S'), 'msj': msj}, context=context)

    def action_printable(self, cr, uid, ids, context={}):
        aids=[]
        invoice =self.browse(cr,uid,ids)[0].invoice_id
        msj =self.browse(cr,uid,ids)[0].msj
        invoice_obj = self.pool.get('account.invoice')
        type=self.browse(cr,uid,ids)[0].type
        (fileno, fname) = tempfile.mkstemp('.pdf', 'openerp_' + (False or '') + '__facturae__' )
        os.close( fileno )
        file = invoice_obj.create_report(cr, uid, [invoice.id], "account.invoice.facturae.webkit", fname)
        adjuntos = self.pool.get('ir.attachment').search(cr, uid, [('res_model','=','account.invoice'),('res_id','=',invoice),('datas_fname','=', invoice.fname_invoice+'.pdf')])
        for attachment in self.browse(cr, uid, adjuntos, context):
            aids= attachment.id
            self.pool.get('ir.attachment').write(cr, uid, attachment.id, { 'name': invoice.fname_invoice + '.pdf', }, context={})
        if aids:
            msj+= "Attached Successfully PDF\n"
        else:
            msj+= "Not Attached PDF\n"
        return self.write(cr, uid, ids, {'state': 'printable', 'file_pdf': aids or False, 'msj': msj, 'last_date': time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)

    def action_send_customer(self, cr, uid, ids, context=None):
        attachments=[]
        msj=''
        attach_name=''
        state=''
        invoice =self.browse(cr,uid,ids)[0].invoice_id
        address_id = self.pool.get('res.partner').address_get(cr, uid, [invoice.partner_id.id], ['invoice'])['invoice']
        partner_invoice_address = self.pool.get('res.partner').browse(cr, uid, address_id, context)
        type=self.browse(cr,uid,ids)[0].type
        msj =self.browse(cr,uid,ids)[0].msj
        fname_invoice = invoice.fname_invoice and invoice.fname_invoice  or ''
        adjuntos = self.pool.get('ir.attachment').search(cr, uid, [('res_model','=','account.invoice'),('res_id','=',invoice)])
        subject = 'Invoice '+invoice.number or False
        for attach in self.pool.get('ir.attachment').browse(cr, uid, adjuntos):
            attachments.append(attach.id)
            attach_name+=attach.name+ ', '
        if release.version >= '7':
            mail_compose_message_pool = self.pool.get('mail.compose.message')
#            mail_tmp_pool = self.pool.get('email.template')
#            tmp_id = mail_tmp_pool.search(cr, uid, [('name','=','FacturaE')], limit=1)
 #           tmp_id = tmp_id and tmp_id[0] or False

            tmp_id = self.get_tmpl_email_id(cr, uid, ids, context=context)
            
            message = mail_compose_message_pool.onchange_template_id(cr, uid, [], template_id=tmp_id, composition_mode=None, model='account.invoice', res_id=invoice.id, context=context)
            mssg = message.get('value', False)
            mssg['partner_ids'] = [(6, 0, mssg['partner_ids'])]
            mssg['attachment_ids'] = [(6, 0, attachments)]
            mssg_id = self.pool.get('mail.compose.message').create(cr, uid, mssg)
            state = self.pool.get('mail.compose.message').send_mail(cr, uid, [mssg_id], context=context)
#            mail=self.pool.get('mail.mail').create(cr, uid, {
 #               'subject': subject+' '+type,
  #              'email_from': email_from,
   #             'email_to': invoice.partner_id.email,
    #            'auto_delete': False,
     #           'body_html': attach_name,
      #          'attachment_ids': [(6, 0, attachments)],
       #         'model': invoice._name,
        #        'record_name': invoice.number,
         #       'res_id': invoice.id,
                #'partner_ids': invoice.partner_id,
          #      }, context=context)
#            state = self.pool.get('mail.mail').send(cr, uid, [mail], auto_commit=False, recipient_ids=None, context=context)
        elif release.version < '7':
            mail=self.pool.get('mail.message').create(cr, uid, {
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
            state = self.pool.get('mail.message').send(cr, uid, [mail], auto_commit=False, context=context)
        if not state:
            msj +='Please Check the Email Configuration!\n'
        else :
            msj +='Email Send Successfully\n'
        return self.write(cr, uid, ids, {'state': 'sent_customer', 'msj': msj, 'last_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    def action_send_backup(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'sent_backup'})

    def action_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'})

    def action_cancel(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        attach_obj = self.pool.get('ir.attachment')
        type=self.browse(cr,uid,ids)[0].type
        invoice =self.browse(cr,uid,ids)[0].invoice_id
        msj = self.browse(cr,uid,ids)[0].msj
        if type=='cfdi32':
            get_file_cancel=invoice_obj._get_file_cancel(cr, uid, [invoice], context = {})
            sf_cancel=invoice_obj.sf_cancel(cr, uid, [invoice.id], context = {})
            msj += tools.ustr(sf_cancel['message'])
        adjuntos = self.pool.get('ir.attachment').search(cr, uid, [('res_model','=','account.invoice'),('res_id','=',invoice)])
        for attachment in self.browse(cr, uid, adjuntos, context):
            ids2=attach_obj.write(cr, uid, attachment.id, { 'res_id': False, }, context={})
        return self.write(cr, uid, ids, {'state': 'cancel','last_date': time.strftime('%Y-%m-%d %H:%M:%S'), 'msj': msj,})

    def reset_to_draft(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for row in self.browse(cr, uid, ids, context=context):
            # Deleting the existing instance of workflow
            wf_service.trg_delete(uid, 'ir.attachment.facturae.mx', row.id, cr)
            wf_service.trg_create(uid, 'ir.attachment.facturae.mx', row.id, cr)
        return self.write(cr, uid, ids, {'state': 'draft'})
    
    def get_tmpl_email_id(self, cr, uid, ids, context=None):
        email_settings = self.pool.get('l10n.mx.email.config.settings')
        cr.execute(""" select max(id) as email_tmp_id from l10n_mx_email_config_settings """)
        dat = cr.dictfetchall()
        email_tmp_id = email_settings.browse(cr, uid, dat[0]['email_tmp_id']).email_tmp_id
        return email_tmp_id and email_tmp_id.id or False
    
ir_attachment_facturae_mx()
