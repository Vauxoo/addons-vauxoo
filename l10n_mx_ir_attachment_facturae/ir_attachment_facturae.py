#!/usr/bin/python
# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Juan Carlos Funes(juan@vauxoo.com)
#
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
#
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools
from openerp import netsvc
from openerp import release
import time
import tempfile
import base64
import os
from openerp import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)
import traceback
import sys
from xml.dom import minidom
import xml.dom.minidom
from pytz import timezone
import pytz
import time
from datetime import datetime, timedelta
try:
    from qrcode import *
except:
    _logger.error('Execute "sudo pip install pil qrcode" to use l10n_mx_facturae_pac_finkok module.')

class ir_attachment_facturae_mx(osv.Model):
    _name = 'ir.attachment.facturae.mx'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _create_qrcode(self, cr, uid, ids, rfc_receiver, rfc_transmitter, amount_total=0, folio_fiscal=False, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        #~ invoice = self.browse(cr, uid, invoice_id)
        #~ rfc_transmitter = invoice.company_id.partner_id.vat_split or ''
        #~ rfc_receiver = invoice.partner_id.parent_id.vat_split or invoice.partner_id.parent_id.vat_split or ''
        #~ amount_total = string.zfill("%0.6f"%invoice.amount_total,17)
        cfdi_folio_fiscal = folio_fiscal or ''
        qrstr = "?re="+rfc_transmitter+"&rr="+rfc_receiver+"&tt="+amount_total+"&id="+cfdi_folio_fiscal
        qr = QRCode(version=1, error_correction=ERROR_CORRECT_L)
        qr.add_data(qrstr)
        qr.make() # Generate the QRCode itself
        im = qr.make_image()
        fname=tempfile.NamedTemporaryFile(suffix='.png',delete=False)
        im.save(fname.name)
        return fname.name

    def _create_original_str(self, cr, uid, ids, result, context=None):
        if context is None:
            context = {}
        #~ ids = isinstance(ids, (int, long)) and [ids] or ids
        #~ invoice = self.browse(cr, uid, invoice_id)
        cfdi_folio_fiscal = result.UUID or ''
        cfdi_fecha_timbrado = result.Fecha or ''
        #~ if cfdi_fecha_timbrado:
            #~ cfdi_fecha_timbrado=time.strftime('%Y-%m-%dT%H:%M:%S', time.strptime(cfdi_fecha_timbrado, '%Y-%m-%d %H:%M:%S'))
        sello = result.SatSeal or ''
        cfdi_no_certificado = result.NoCertificadoSAT or ''
        original_string = '||1.0|'+cfdi_folio_fiscal+'|'+str(cfdi_fecha_timbrado)+'|'+sello+'|'+cfdi_no_certificado+'||'
        return original_string

    def _get_type(self, cr, uid, ids=None, context=None):
        if context is None:
            context = {}
        types = []
        return types

    def get_driver_fc_sign(self):
        """function to inherit from module driver of pac and add particular function"""
        return {}

    def get_driver_fc_cancel(self):
        """function to inherit from module driver of pac and add particular function"""
        return {}

    _columns = {
        'name': fields.char('Name', size=128, required=True, readonly=True,
                            help='Name of attachment generated'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True,
                                      help='Invoice to which it belongs this attachment'),
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
            ('cancel', 'Cancelled'), ],
            'State', readonly=True, required=True, help='State of attachments'),
        'journal_id': fields.many2one('account.journal','Journal', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'user_pac': fields.char('User PAC', size=128, help='Name user for login to PAC'),
        'password_pac': fields.char('Password PAC', size=128, help='Password user for login to PAC'),
        'url_webservice_pac': fields.char('URL WebService', size=256, help='URL of WebService used for send to sign the XML to PAC'),
        'certificate_link': fields.char('Certificate link', size=256 , 
            help='PAC have a public certificate that is necessary by customers to check the validity of the XML and PDF'),
        'certificate_file': fields.binary('Certificate File',
            filters='*.cer,*.certificate,*.cert', help='This file .cer is proportionate by the SAT'),
        'certificate_key_file': fields.binary('Certificate Key File',
            filters='*.key', help='This file .key is proportionate by the SAT'),
        'certificate_password': fields.char('Certificate Password', size=64,
            invisible=False, help='This password is proportionate by the SAT'),
        'attachment_email': fields.char('Email', size=128, help='Email receptor'),
        'cfdi_folio_fiscal': fields.char('Folio Fiscal(UUID)', size=256, help='UUID the XML'),
        'model_source': fields.char('Source Model', size=128, help='Source Model'),
        'id_source': fields.integer('Source ID', help="Source ID"),
        'company_emitter_id': fields.many2one('res.company', 'Company emmiter'),
        'certificate_id': fields.many2one('res.company.facturae.certificate'),
        'cfdi_cbb': fields.binary('CFD-I CBB'),
        'cfdi_sello': fields.text('CFD-I Sello', help='Sign assigned by the SAT'),
        'cfdi_no_certificado': fields.char('CFD-I Certificado', size=32,
                                           help='Serial Number of the Certificate'),
        'cfdi_cadena_original': fields.text('CFD-I Cadena Original',
                                            help='Original String used in the electronic invoice'),
        'cfdi_fecha_timbrado': fields.datetime('CFD-I Fecha Timbrado',
                                               help='Date when is stamped the electronic invoice'),
        'cfdi_fecha_cancelacion': fields.datetime('CFD-I Fecha Cancelacion',
                                                  help='If the invoice is cancel, this field saved the date when is cancel'),
        'pac_id': fields.many2one('params.pac', 'Pac', help='Pac used in singned of the invoice'),
        'cadena_original': fields.text('String Original', size=512,
            help='Data stream with the information contained in the electronic \
            invoice'),
        'document_source': fields.char('Document Source', size=128, help='Number or reference of document source'),
    }

    _defaults = {
        'state': 'draft',
        'company_id': lambda self, cr, uid, c:
        self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        'last_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    def create_ir_attachment_facturae(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        status = False
        try:
            cr.execute("SAVEPOINT ir_attachment_facturae_mx_savepoint")
            status = self.signal_confirm(cr, uid, ids, context=context)
            cr.execute("RELEASE SAVEPOINT ir_attachment_facturae_mx_savepoint")
            cr.execute("SAVEPOINT ir_attachment_facturae_mx_savepoint")
            self.signal_sign(cr, uid, ids, context=context)
            cr.execute("RELEASE SAVEPOINT ir_attachment_facturae_mx_savepoint")
            cr.execute("SAVEPOINT ir_attachment_facturae_mx_savepoint")
            self.signal_printable(cr, uid, ids, context=context)
            cr.execute("RELEASE SAVEPOINT ir_attachment_facturae_mx_savepoint")
            cr.execute("SAVEPOINT ir_attachment_facturae_mx_savepoint")
            self.signal_send_customer(cr, uid, ids, context=context)
            cr.execute("RELEASE SAVEPOINT ir_attachment_facturae_mx_savepoint")
            cr.execute("SAVEPOINT ir_attachment_facturae_mx_savepoint")
            self.signal_send_backup(cr, uid, ids, context=context)
            cr.execute("RELEASE SAVEPOINT ir_attachment_facturae_mx_savepoint")
            cr.execute("SAVEPOINT ir_attachment_facturae_mx_savepoint")
            self.signal_done(cr, uid, ids, context=context)
            cr.execute("RELEASE SAVEPOINT ir_attachment_facturae_mx_savepoint")
            status = True
        except Exception, e:
            cr.execute("ROLLBACK TO SAVEPOINT ir_attachment_facturae_mx_savepoint")
            error = tools.ustr(traceback.format_exc())
            self.write(cr, uid, ids, {'msj': error}, context=context)
            _logger.error(error)
        return status

    def signal_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        from l10n_mx_facturae_lib import facturae_lib
        msj, app_xsltproc_fullpath, app_openssl_fullpath, app_xmlstarlet_fullpath = facturae_lib.library_openssl_xsltproc_xmlstarlet(cr, uid, ids, context)
        if msj:
            raise osv.except_osv(_('Warning'),_(msj))
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        attachment_obj = self.pool.get('ir.attachment')
        wf_service = netsvc.LocalService("workflow")
        msj = ''
        for attach in self.browse(cr, uid, ids, context=context):
            id_source = attach.id_source
            model_source = attach.model_source
            type = attach.type
            fname = str(attach.id) + '_XML_V3_2.xml' or ''
            attachment_id = attachment_obj.create(cr, uid, {
                'name': fname,
                'datas': attach.file_input_index,
                'datas_fname': fname,
                'res_model': model_source or False,
                'res_id': id_source or False,
            }, context=context)
            if attachment_id:
                msj = _("Attached Successfully XML CFD 3.2.")
            xml_data = base64.decodestring(attach.file_input_index)
            doc_xml = xml.dom.minidom.parseString(xml_data)
            index_xml = doc_xml.toprettyxml()
            self.write(cr, uid, ids,
                       {'file_input': attachment_id or False,
                           'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                           'msj': msj,
                           'file_input_index': index_xml or ''}, context=context)
            wf_service.trg_validate(uid, self._name, ids[0], 'action_confirm', cr)
            return True

    def action_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        return self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)

    def signal_sign(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        attachment_obj = self.pool.get('ir.attachment')
        wf_service = netsvc.LocalService("workflow")
        attach = ''
        index_xml = ''
        msj = ''
        status = False
        for data in self.browse(cr, uid, ids, context=context):
            type = data.type
            id_source = data.id_source
            model_source = data.model_source
            attach_v3_2 = data.file_input and data.file_input.id or False
            index_content = data.file_input and data.file_input.index_content.encode('utf-8') or False
            type__fc = self.get_driver_fc_sign()
            if type in type__fc.keys():
                fname_invoice = data.name and data.name + '.xml' or ''
                fdata = base64.encodestring(index_content)
                res = type__fc[type](cr, uid, [data.id], fdata, context=context)
                msj = tools.ustr(res.get('msg', False))
                index_xml = res.get('cfdi_xml', False)
                status = res.get('status', False)
                if status:
                    data_attach = {
                        'name': fname_invoice,
                        'datas': base64.encodestring(res.get('cfdi_xml', False)),
                        'datas_fname': fname_invoice,
                        'description': 'XML CFD-I SIGN',
                        'res_model': model_source,
                        'res_id': id_source,
                    }
                    attach = attachment_obj.create(cr, uid, data_attach, context=None)
                    if attach_v3_2:
                        cr.execute("""UPDATE ir_attachment
                            SET res_id = Null
                            WHERE id = %s""", (attach_v3_2,))
                    doc_xml = xml.dom.minidom.parseString(index_xml)
                    index_xml = doc_xml.toprettyxml()
                    self.write(cr, uid, ids,
                           {'file_xml_sign': attach or False,
                               'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                               'msj': msj,
                               'file_xml_sign_index': index_xml}, context=context)
                    wf_service.trg_validate(uid, self._name, data.id, 'action_sign', cr)
                    status = True
            else:
                msj += _("Unknow driver for %s" % (type))
                status = False
        return status

    def action_sign(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'signed'}, context=context)

    def signal_printable(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        aids = ''
        msj = ''
        index_pdf = ''
        attachment_obj = self.pool.get('ir.attachment')
        attachment_mx_data = self.browse(cr, uid, ids)
        type = self.browse(cr, uid, ids)[0].type
        wf_service = netsvc.LocalService("workflow")
        status = False
        (fileno, fname) = tempfile.mkstemp(
            '.pdf', 'openerp_pdfcfid_' + (str(attachment_mx_data[0].id) or '') + '__facturae__')
        os.close(fileno)
        report_multicompany_obj = self.pool.get('report.multicompany')
        report_ids = report_multicompany_obj.search(
            cr, uid, [('model', '=', 'ir.attachment.facturae.mx')], limit=1) or False
        report_name = 'account.invoice.facturae.webkit'
        if report_ids:
            report_name = report_multicompany_obj.browse(cr, uid, report_ids[0]).report_name
        service = netsvc.LocalService("report."+report_name)
        (result, format) = service.create(cr, SUPERUSER_ID, [attachment_mx_data[0].id], report_name, context=context)                
        attachment_ids = attachment_obj.search(cr, uid, [('res_model', '=', self._name),('res_id', '=', attachment_mx_data[0].id)])
        file_name_attachment = attachment_obj.browse(cr, uid, attachment_ids, context=context)[0].datas_fname
        for attachment in self.browse(cr, uid, attachment_ids, context=context):
            # TODO: aids.append( attachment.id ) but without error in last
            # write
            
            aids = attachment.id
            
            attachment_obj.write(cr, uid, [attachment.id], {
                'name': file_name_attachment }, context=context)
            status = True
        if status and aids:
            msj = _("Attached Successfully PDF\n")
            self.write(cr, uid, ids, {
                'file_pdf': aids or False,
                'msj': msj,
                'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'file_pdf_index': index_pdf}, context=context)
            wf_service.trg_validate(uid, self._name, ids[0], 'action_printable', cr)
        else:
            raise osv.except_osv(_('Warning'), _('Not Attached PDF\n'))
        return status

    def action_printable(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'printable'}, context=context)

    def signal_send_customer(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        attachments = []
        msj = ''
        state = ''
        partner_mail = ''
        user_mail = ''
        status = False
        data = self.browse(cr, uid, ids)[0]
        company_id = data.company_id and data.company_id.id or False
        wf_service = netsvc.LocalService("workflow")
        attachments = []
        data.file_pdf and attachments.append(data.file_pdf.id)
        data.file_xml_sign and attachments.append(data.file_xml_sign.id)
        obj_ir_mail_server = self.pool.get('ir.mail_server')
        obj_mail_mail = self.pool.get('mail.mail')
        obj_users = self.pool.get('res.users')
        mail_server_id = obj_ir_mail_server.search(cr, uid,
                                                   ['|', ('company_id', '=', company_id), ('company_id', '=', False)], limit=1, order='sequence', context=None)
        if mail_server_id:
            for smtp_server in obj_ir_mail_server.browse(cr, uid,
                                                         mail_server_id, context=context):
                server_name = smtp_server.name
                smtp = False
                try:
                    smtp = obj_ir_mail_server.connect(
                        smtp_server.smtp_host, smtp_server.smtp_port,
                        user=smtp_server.smtp_user,
                        password=smtp_server.smtp_pass,
                        encryption=smtp_server.smtp_encryption,
                        smtp_debug=smtp_server.smtp_debug)
                except Exception, e:
                    raise osv.except_osv(_("Connection test failed!"), _(
                        "Configure outgoing mail server named FacturaE:\n %s") % tools.ustr(e))
            mail_compose_message_pool = self.pool.get('mail.compose.message')
            email_pool = self.pool.get('email.template')

            tmp_id = email_pool.search(cr, uid, [(
                    'model_id.model', '=', self._name),
                    ('company_id', '=', company_id),
                    ('mail_server_id', '=', smtp_server.id),
                    ], limit=1, context=context)
            if tmp_id:
                message = mail_compose_message_pool.onchange_template_id(
                    cr, uid, [], template_id=tmp_id[
                        0], composition_mode=None,
                    model = self._name, res_id = data.id, context=context)
                mssg = message.get('value', False)
                user_mail = obj_users.browse(
                    cr, uid, uid, context=None).email
                partner_id = mssg.get('partner_ids', False)
                partner_mail = data.attachment_email
                if partner_mail:
                    if user_mail:
                        if mssg.get('partner_ids', False) and tmp_id:
                            mssg['partner_ids'] = [
                                (6, 0, mssg['partner_ids'])]
                            mssg['attachment_ids'] = [
                                (6, 0, attachments)]
                            mssg_id = self.pool.get(
                                'mail.compose.message').create(cr, uid, mssg, context=None)
                            state = self.pool.get('mail.compose.message').send_mail(
                                cr, uid, [mssg_id], context=context)
                            asunto = mssg['subject']
                            id_mail = obj_mail_mail.search(
                                cr, uid, [('subject', '=', asunto)])
                            if id_mail:
                                for mail in obj_mail_mail.browse(cr, uid, id_mail, context=None):
                                    if mail.state == 'exception':
                                        msj = _(
                                            '\nNot correct email of the user or customer. Check in Menu Configuración\Tecnico\Email\Emails\n')
                                        raise osv.except_osv(_('Warning'), _('Not correct email of the user or customer. Check in Menu Configuración\Tecnico\Email\Emails'))
                                msj = _('Email Send Successfully.Attached is sent to %s for Outgoing Mail Server %s') % (
                                partner_mail, server_name)
                                self.write(cr, uid, ids, {
                                        'msj': msj,
                                        'last_date': time.strftime('%Y-%m-%d %H:%M:%S')})
                                wf_service.trg_validate(
                                        uid, self._name, ids[0], 'action_send_customer', cr)
                                status = True
                            else:
                                msj = _('Email Send Successfully.Attached is sent to %s for Outgoing Mail Server %s') % (
                                partner_mail, server_name)
                                self.write(cr, uid, ids, {
                                        'msj': msj,
                                        'last_date': time.strftime('%Y-%m-%d %H:%M:%S')})
                                wf_service.trg_validate(
                                        uid, self._name, ids[0], 'action_send_customer', cr)
                                status = True
                    else:
                        raise osv.except_osv(
                            _('Warning'), _('This user does not have mail'))
                else:
                    raise osv.except_osv(
                        _('Warning'), _('The attachment does not have mail'))
            else:
                raise osv.except_osv(
                    _('Warning'), _('Check that your template is assigned outgoing mail server named %s.\nAlso the field has report_template = Factura Electronica Report.\nTemplate is associated with the same company') % (server_name))
        else:
            raise osv.except_osv(_('Warning'), _('Not Found\
            outgoing mail server.Configure the outgoing mail server named "FacturaE"'))
        return status

    def action_send_customer(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'sent_customer'}, context=context)

    def signal_send_backup(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        msj = ''
        wf_service = netsvc.LocalService("workflow")
        msj = _('Send Backup\n')
        self.write(cr, uid, ids, {'msj': msj,
                                  'last_date': time.strftime('%Y-%m-%d %H:%M:%S')
                                  }, context=context)
        wf_service.trg_validate(uid, self._name, ids[0], 'action_send_backup', cr)
        return True

    def action_send_backup(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'sent_backup'}, context=context)

    def signal_done(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        msj = ''
        wf_service = netsvc.LocalService("workflow")
        msj = _('Done\n')
        self.write(cr, uid, ids, {'msj': msj,
                                  'last_date': time.strftime('%Y-%m-%d %H:%M:%S')
                                  }, context=context)
        wf_service.trg_validate(uid, self._name, ids[0], 'action_done', cr)
        return True


    def action_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)

    def signal_cancel(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        attach_obj = self.pool.get('ir.attachment')
        wf_service = netsvc.LocalService("workflow")
        status = False
        status_stamp = False
        res = False
        for ir_attach_facturae_mx_id in self.browse(cr, uid, ids, context=context):
            msj = ''
            invoice = ir_attach_facturae_mx_id.invoice_id
            if invoice.state != 'cancel':
                res = invoice_obj.action_cancel(cr, uid, [invoice.id])
            else:
                #wf_service.trg_validate(uid, 'account.invoice', invoice.id, 'invoice_cancel', cr)
                if 'cfdi' in ir_attach_facturae_mx_id.type:
                    if not ir_attach_facturae_mx_id.state in ['cancel', 'draft', 'confirmed']:
                        type__fc = self.get_driver_fc_cancel()
                        if ir_attach_facturae_mx_id.type in type__fc.keys():
                            cfdi_cancel = res = type__fc[ir_attach_facturae_mx_id.type](
                                cr, uid, [
                                    ir_attach_facturae_mx_id.id], context=context
                            )
                            msj += tools.ustr(cfdi_cancel.get('message', False))
                            status_stamp = cfdi_cancel.get('status', False)
                            if status_stamp:
                                cr.execute("""UPDATE ir_attachment SET res_id = Null
                                        WHERE res_id = %s and res_model='account.invoice'""", (invoice.id,))
                                wf_service.trg_validate(
                                    uid, self._name, ir_attach_facturae_mx_id.id, 'action_cancel', cr)
                                status = True
                            else:
                                status = False
                        else:
                            msj = _("Unknow cfdi driver for %s" % (ir_attach_facturae_mx_id.type))
                    else:
                        wf_service.trg_validate(
                            uid, self._name, ir_attach_facturae_mx_id.id, 'action_cancel', cr)
                        cr.execute("""UPDATE ir_attachment SET res_id = Null
                                WHERE res_id = %s and res_model='account.invoice'""", (invoice.id,))
                        status = True
                        msj = 'cancelled'
                elif 'cfd' in ir_attach_facturae_mx_id.type and not 'cfdi' in ir_attach_facturae_mx_id.type:
                    wf_service.trg_validate(
                                    uid, self._name, ir_attach_facturae_mx_id.id, 'action_cancel', cr)
                    inv_cancel_status = invoice_obj.action_cancel(cr, uid, [invoice.id], context=context)
                    msj = 'cancelled'
                    status = True
                elif 'cbb' in ir_attach_facturae_mx_id.type:
                    wf_service.trg_validate(
                                    uid, self._name, ir_attach_facturae_mx_id.id, 'action_cancel', cr)
                    inv_cancel_status = invoice_obj.action_cancel(cr, uid, [invoice.id], context=context)
                    msj = 'cancelled'
                    status = True
                else:
                    raise osv.except_osv(_("Type Electronic Invoice Unknow!"), _(
                        "The Type Electronic Invoice:" + (ir_attach_facturae_mx_id.type or '')))
                if status:
                    self.write(cr, uid, ids, {
                           'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                           'msj': msj,
                           })
        return status

    def action_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=context)

    def reset_to_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for row in ids:
            # Deleting the existing instance of workflow
            wf_service.trg_delete(uid, self._name, row, cr)
            wf_service.trg_create(uid, self._name, row, cr)
        return True

    def forward_email(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        try:
            self.signal_send_customer(cr, uid, ids, context=context)
            msj = _('Forward Email')
            self.write(cr, uid, ids, {'msj': msj,
                                      'last_date': time.strftime('%Y-%m-%d %H:%M:%S')
                                      }, context=context)
            status_forward = True
        except Exception, e:
            error = tools.ustr(traceback.format_exc())
            self.write(cr, uid, ids, {'msj': error}, context=context)
            _logger.error(error)
            status_forward = False
        return status_forward
        
    def _get_time_zone(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res_users_obj = self.pool.get('res.users')
        userstz = res_users_obj.browse(cr, uid, [uid])[0].partner_id.tz
        a = 0
        if userstz:
            hours = timezone(userstz)
            fmt = '%Y-%m-%d %H:%M:%S %Z%z'
            now = datetime.now()
            loc_dt = hours.localize(datetime(now.year, now.month, now.day,
                                             now.hour, now.minute, now.second))
            timezone_loc = (loc_dt.strftime(fmt))
            diff_timezone_original = timezone_loc[-5:-2]
            timezone_original = int(diff_timezone_original)
            s = str(datetime.now(pytz.timezone(userstz)))
            s = s[-6:-3]
            timezone_present = int(s)*-1
            a = timezone_original + ((
                timezone_present + timezone_original)*-1)
        return a


class ir_attachment(osv.Model):
    _inherit = 'ir.attachment'

    def unlink(self, cr, uid, ids, context=None):
        attachments = self.pool.get(
            'ir.attachment.facturae.mx').search(cr, SUPERUSER_ID, ['|',
                                                                   '|', ('file_input', 'in', ids), ('file_xml_sign', 'in', ids), ('file_pdf', 'in',
                                                                                                                                  ids)])
        if attachments:
            raise osv.except_osv(_('Warning!'), _(
                'You can not remove an attachment of an invoice'))
        return super(ir_attachment, self).unlink(cr, uid, ids, context=context)


class ir_mail_server(osv.Model):
    _inherit = 'ir.mail_server'

    def send_email(
        self, cr, uid, message, mail_server_id=None, smtp_server=None, smtp_port=None,
        smtp_user=None, smtp_password=None, smtp_encryption=None, smtp_debug=False,
            context=None):
        obj_ir_mail_server = self.pool.get('ir.mail_server')
        company_id = self.pool.get('res.users').browse(
            cr, uid, uid, context=context).company_id.id
        mail_server_id = obj_ir_mail_server.search(cr, uid,
                                                   ['|', ('company_id', '=', company_id), ('company_id', '=', False)], limit=1, order='sequence', context=None)[0]
        super(
            ir_mail_server, self).send_email(cr, uid, message, mail_server_id=mail_server_id, smtp_server=None, smtp_port=None,
                                             smtp_user=None, smtp_password=None, smtp_encryption=None, smtp_debug=False,
                                             context=None)
        return True
