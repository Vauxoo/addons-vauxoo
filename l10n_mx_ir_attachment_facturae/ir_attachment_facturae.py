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
import tools
import time
from osv import fields, osv, orm
import tempfile
import base64
import os
import netsvc

class ir_attachment_facturae_mx(osv.osv):
    _name = 'ir.attachment.facturae.mx'

    def _get_type(self, cr, uid, ids=None, context=None):
        types = [('cfd22', 'CFD 2.2'), ('cbb', 'CBB'),('cfdi32', 'CFDI 3.2 Solución Factible'),]
        return types

    _columns = {
        'name': fields.char('Name', size=128, required=True, readonly=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        #'pac_id': ,Ver si no genera dependencia del modelo de pac
        'file_input': fields.many2one('ir.attachment', 'File input'),#TODO: Agregar readonly dependiendo del state
        'file_input_index': fields.text('File input'),
        'file_xml_sign': fields.many2one('ir.attachment', 'File XML Sign'),
        'file_xml_sign_index': fields.text('File XML Sign Index'),
        'file_pdf': fields.many2one('ir.attachment', 'File PDF'),
        'file_pdf_index': fields.text('File PDF Index'),
        'identifier': fields.char('Identifier', size=128),
        'type': fields.selection(_get_type, 'Type', type='char', size=64, readonly=True),
        'description': fields.text('Description'),
        #'invoice_type': fields.ref(),#referencia al tipo de factura
        'msj': fields.text('Last Message', readonly=True),
        'last_date': fields.datetime('Last Modified', readonly=True),
        'state': fields.selection([
                ('draft', 'Draft'),
                ('confirmed', 'Confirmed'),#Generate XML
                ('signed', 'Signed'),#Generate XML Sign
                ('printable', 'Printable Format Generated'),#Generate PDF
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
        aids=[]
        invoice =self.browse(cr,uid,ids)[0].invoice_id
        invoice_obj = self.pool.get('account.invoice')
        type=self.browse(cr,uid,ids)[0].type
        fname_invoice = invoice.fname_invoice and invoice.fname_invoice + '.xml' or ''
        if type=='cfd22':
            fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(cr, uid, [invoice.id] , context=context)
            attach=self.pool.get('ir.attachment').create(cr, uid, {
                'name': fname_invoice,
                'datas': base64.encodestring(xml_data),
                'datas_fname': fname_invoice,
                'res_model': 'account.invoice',
                'res_id': invoice.id,
                }, context=context)
        if type=='cfdi32':
            fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(cr, uid, [invoice.id] , context=context)
            attach=self.pool.get('ir.attachment').create(cr, uid, {
                'name': fname_invoice,
                'datas': base64.encodestring(xml_data),
                'datas_fname': fname_invoice,
                'res_model': 'account.invoice',
                'res_id': invoice.id,
                }, context=context)
        if attach:
            msj="Attached Successfully XML"
        else:
            msj="Error"
        return self.write(cr, uid, ids, {'state': 'confirmed', 'file_input': attach or False, 'last_date': time.strftime('%Y-%m-%d %H:%M:%S'), 'msj': msj}, context=context)

    def action_sign(self, cr, uid, ids, context={}):
        aids=[]
        xml_v3_2=[]
        invoice =self.browse(cr,uid,ids)[0].invoice_id
        invoice_obj = self.pool.get('account.invoice')
        type=self.browse(cr,uid,ids)[0].type
        res= {'msg':''}
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
            msj='Attached Successfully XML'
            res['msg'] = msj
        if type=='cfdi32':
            fname_invoice = invoice.fname_invoice and invoice.fname_invoice + '.V2.2.xml' or ''
            fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(cr, uid, [invoice.id] , context=context)
            attach=self.pool.get('ir.attachment').create(cr, uid, {
                'name': fname_invoice,
                'datas': base64.encodestring(xml_data),
                'datas_fname': fname_invoice,
                'res_model': 'account.invoice',
                #'res_id': invoice.id,
                }, context=context)
            fdata = base64.encodestring( xml_data )
            res = invoice_obj._upload_ws_file(cr, uid, [invoice.id], fdata, context={})
            xml_v3_2 = self.pool.get('ir.attachment').search(cr, uid, [('datas_fname','=', invoice.fname_invoice+'.xml'),('res_model','=','account.invoice'),('res_id','=',invoice.id)])[0]
        return self.write(cr, uid, ids, {'state': 'signed', 'file_xml_sign': xml_v3_2 or False, 'file_input': attach or False, 'last_date': time.strftime('%Y-%m-%d %H:%M:%S'), 'msj': res['msg']}, context=context)

    def action_printable(self, cr, uid, ids, context={}):
        aids=[]
        invoice =self.browse(cr,uid,ids)[0].invoice_id
        invoice_obj = self.pool.get('account.invoice')
        type=self.browse(cr,uid,ids)[0].type
        (fileno, fname) = tempfile.mkstemp('.pdf', 'openerp_' + (False or '') + '__facturae__' )
        os.close( fileno )
        if type=='cfd22':
            file = invoice_obj.create_report(cr, uid, [invoice.id], "account.invoice.facturae.pdf", fname)
            fname_invoice = invoice.fname_invoice and invoice.fname_invoice + '.pdf' or ''
            is_file = file[0]
            fname = file[1]
            #if is_file and os.path.isfile(fname_invoice):
            if is_file and os.path.isfile(fname):
                f = open(fname, "r")
                data = f.read()
                f.close()
                data_attach = {
                    'name': invoice.fname_invoice,
                    'datas': data and base64.encodestring( data ) or None,
                    'datas_fname': fname_invoice,
                    'description': 'Factura_PDF_CFD',
                    'res_model': invoice_obj._name,
                    'res_id': invoice.id,
                }
                self.pool.get('ir.attachment').create(cr, uid, data_attach, context=context)

            aids = self.pool.get('ir.attachment').search(cr, uid, [('datas_fname','=',invoice.fname_invoice+'.pdf'),('res_model','=','account.invoice'),('res_id','=',invoice.id)])[0]
        if type=='cfdi32':
            file = invoice_obj.create_report(cr, uid, [invoice.id], "account.invoice.facturae.pac.sf.pdf", fname)
            fname_invoice = invoice.fname_invoice and invoice.fname_invoice + '.pdf' or ''
            is_file = file[0]
            fname = file[1]
            #if is_file and os.path.isfile(fname_invoice):
            if is_file and os.path.isfile(fname):
                f = open(fname, "r")
                data = f.read()
                f.close()
                data_attach = {
                    'name': invoice.fname_invoice,
                    'datas': data and base64.encodestring( data ) or None,
                    'datas_fname': fname_invoice,
                    'description': 'Factura_PDF_CFDI_SF',
                    'res_model': invoice_obj._name,
                    'res_id': invoice.id,
                }
                self.pool.get('ir.attachment').create(cr, uid, data_attach, context=context)
            aids = self.pool.get('ir.attachment').search(cr, uid, [('datas_fname','=',invoice.fname_invoice+'.pdf'),('res_model','=','account.invoice'),('res_id','=',invoice.id)])[0]
        if type=='cbb':
            file = invoice_obj.create_report(cr, uid, [invoice.id], "account.invoice.facturae.pdf2", fname)
            fname_invoice = invoice.fname_invoice and invoice.fname_invoice + '.pdf' or ''
            is_file = file[0]
            fname = file[1]
            #if is_file and os.path.isfile(fname_invoice):
            if is_file and os.path.isfile(fname):
                f = open(fname, "r")
                data = f.read()
                f.close()
                data_attach = {
                    'name': invoice.fname_invoice,
                    'datas': data and base64.encodestring( data ) or None,
                    'datas_fname': fname_invoice,
                    'description': 'Factura_PDF_CBB',
                    'res_model': invoice_obj._name,
                    'res_id': invoice.id,
                }
                self.pool.get('ir.attachment').create(cr, uid, data_attach, context=context)
            aids = self.pool.get('ir.attachment').search(cr, uid, [('datas_fname','=',invoice.fname_invoice+'.pdf'),('res_model','=','account.invoice'),('res_id','=',invoice.id)])[0]
        if aids:
            msj="Attached Successfully PDF"
        else:
            msj="No existe PDF"
        return self.write(cr, uid, ids, {'state': 'printable', 'file_pdf': aids or False , 'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),'msj': msj}, context=context)

    def action_send_customer(self, cr, uid, ids, context=None):
        attachments=[]
        attach_name=''
        to=''
        invoice =self.browse(cr,uid,ids)[0].invoice_id
        smtp= self.pool.get('email.smtpclient').browse(cr, uid, uid, context).id
        fname_invoice = invoice.fname_invoice and invoice.fname_invoice  or ''
        adjuntos = self.pool.get('ir.attachment').search(cr, uid, [('res_model','=','account.invoice'),('res_id','=',invoice)])
        for attach in self.pool.get('ir.attachment').browse(cr, uid, adjuntos):
            f_name = tempfile.gettempdir() +'/'+ attach.name
            open(f_name,'wb').write(base64.decodestring(attach.datas))
            attachments.append(f_name)
            attach_name+=attach.name+ ', '
        print invoice.address_invoice_id.type
        if invoice.address_invoice_id.type=='invoice':
            to=invoice.address_invoice_id.email
        subject= 'Invoice '+invoice.number or False
        message = attach_name
        state = self.pool.get('email.smtpclient').send_email(cr, uid, smtp, to, tools.ustr(subject), tools.ustr(message), attachments)
        if not state:
            msj='Please Check the Server Configuration!'
        else :
            msj='Email Send Successfully'
        return self.write(cr, uid, ids, {'state': 'sent_customer', 'last_date': time.strftime('%Y-%m-%d %H:%M:%S'), 'msj': msj})

    def action_send_backup(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'sent_backup'})

    def action_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'})

    def action_cancel(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        attach_obj = self.pool.get('ir.attachment')
        type=self.browse(cr,uid,ids)[0].type
        invoice =self.browse(cr,uid,ids)[0].invoice_id
        if type=='cfdi32':
            get_file_cancel=invoice_obj._get_file_cancel(cr, uid, [invoice], context = {})
            sf_cancel=invoice_obj.sf_cancel(cr, uid, [invoice.id], context = {})
            msj=sf_cancel['message']
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
ir_attachment_facturae_mx()
