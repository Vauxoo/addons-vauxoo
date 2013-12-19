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


class ir_attachment_facturae_mx(osv.Model):
    _name = 'ir.attachment.facturae.mx'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

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
        if not self.signal_confirm(cr, uid, ids, context=context):
            return False
        if not self.signal_sign(cr, uid, ids, context=context):
            return False
        if not self.signal_printable(cr, uid, ids, context=context):
            return False
        if not self.signal_send_customer(cr, uid, ids, context=context):
            return False
        if not self.signal_send_backup(cr, uid, ids, context=context):
            return False
        if not self.signal_done(cr, uid, ids, context=context):
            return False
        return True

    def signal_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        from l10n_mx_facturae_lib import facturae_lib
        msj, app_xsltproc_fullpath, app_openssl_fullpath, app_xmlstarlet_fullpath = facturae_lib.library_openssl_xsltproc_xmlstarlet(cr, uid, ids, context)
        if msj:
            raise osv.except_osv(_('Warning'),_(msj))
        try:
            if context is None:
                context = {}
            ids = isinstance(ids, (int, long)) and [ids] or ids
            invoice_obj = self.pool.get('account.invoice')
            attach = ''
            msj = ''
            index_xml = ''
            attach = self.browse(cr, uid, ids[0])
            invoice = attach.invoice_id
            type = attach.type
            wf_service = netsvc.LocalService("workflow")
            save_attach = None
            if 'cbb' in type:
                msj = _("Confirmed")
                save_attach = False
            elif 'cfdi' in type:
                fname_invoice = invoice.fname_invoice and invoice.fname_invoice + \
                    '_V3_2.xml' or ''
                fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(
                    cr, uid, [invoice.id], context=context)
                attach = self.pool.get('ir.attachment').create(cr, uid, {
                    'name': fname_invoice,
                    'datas': base64.encodestring(xml_data),
                    'datas_fname': fname_invoice,
                    'res_model': 'account.invoice',
                    'res_id': invoice.id,
                }, context=None)
                msj = _("Attached Successfully XML CFDI 3.2\n")
                save_attach = True
            elif 'cfd' in type and not 'cfdi' in type:
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
                }, context=None)
                if attach:
                    index_xml = self.pool.get('ir.attachment').browse(
                        cr, uid, attach).index_content
                    msj = _("Attached Successfully XML CFD 2.2")
                save_attach = True
            else:
                raise osv.except_osv(_("Type Electronic Invoice Unknow!"), _(
                    "The Type Electronic Invoice:" + (type or '')))
            if save_attach:
                self.write(cr, uid, ids,
                           {'file_input': attach or False,
                               'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                               'msj': msj,
                               'file_xml_sign_index': index_xml}, context=context)
            wf_service.trg_validate(
                uid, self._name, ids[0], 'action_confirm', cr)
            return True
        except Exception, e:
            error = tools.ustr(traceback.format_exc())
            self.write(cr, uid, ids, {'msj': error}, context=context)
            _logger.error(error)
            return False

    def action_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        return self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)

    def signal_sign(self, cr, uid, ids, context=None):
        try:
            if context is None:
                context = {}
            ids = isinstance(ids, (int, long)) and [ids] or ids
            invoice_obj = self.pool.get('account.invoice')
            attachment_obj = self.pool.get('ir.attachment')
            attach = ''
            index_xml = ''
            msj = ''
            for data in self.browse(cr, uid, ids, context=context):
                invoice = data.invoice_id
                type = data.type
                wf_service = netsvc.LocalService("workflow")
                attach_v3_2 = data.file_input and data.file_input.id or False
                if 'cbb' in type:
                    msj = _("Signed")
                if 'cfd' in type and not 'cfdi' in type:
                    attach = data.file_input and data.file_input.id or False
                    index_xml = data.file_xml_sign_index or False
                    msj = _("Attached Successfully XML CFD 2.2\n")
                if 'cfdi' in type:
                    # upload file in custom module for pac
                    type__fc = self.get_driver_fc_sign()
                    if type in type__fc.keys():
                        fname_invoice = invoice.fname_invoice and invoice.fname_invoice + \
                            '.xml' or ''
                        fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(
                            cr, uid, [invoice.id], context=context)
                        fdata = base64.encodestring(xml_data)
                        res = type__fc[type](cr, uid, [data.id], fdata, context=context)
                        msj = tools.ustr(res.get('msg', False))
                        index_xml = res.get('cfdi_xml', False)
                        data_attach = {
                            'name': fname_invoice,
                            'datas': base64.encodestring(res.get('cfdi_xml', False)),
                            'datas_fname': fname_invoice,
                            'description': 'Factura-E XML CFD-I SIGN',
                            'res_model': 'account.invoice',
                            'res_id': invoice.id,
                        }
                        # Context, because use a variable type of our code but we
                        # dont need it.
                        attach = attachment_obj.create(cr, uid, data_attach, context=None)
                        if attach_v3_2:
                            cr.execute("""UPDATE ir_attachment
                                SET res_id = Null
                                WHERE id = %s""", (attach_v3_2,))
                    else:
                        msj += _("Unknow driver for %s" % (type))
                self.write(cr, uid, ids,
                           {'file_xml_sign': attach or False,
                               'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                               'msj': msj,
                               'file_xml_sign_index': index_xml}, context=context)
                wf_service.trg_validate(uid, self._name, data.id, 'action_sign', cr)
                return True
        except Exception, e:
            error = tools.ustr(traceback.format_exc())
            self.write(cr, uid, ids, {'msj': error}, context=context)
            _logger.error(error)
            return False

    def action_sign(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'signed'}, context=context)

    def signal_printable(self, cr, uid, ids, context=None):
        try:
            if context is None:
                context = {}
            aids = ''
            msj = ''
            index_pdf = ''
            attachment_obj = self.pool.get('ir.attachment')
            invoice = self.browse(cr, uid, ids)[0].invoice_id
            invoice_obj = self.pool.get('account.invoice')
            type = self.browse(cr, uid, ids)[0].type
            wf_service = netsvc.LocalService("workflow")
            (fileno, fname) = tempfile.mkstemp(
                '.pdf', 'openerp_' + (invoice.fname_invoice or '') + '__facturae__')
            os.close(fileno)
            #~ report = invoice_obj.create_report(cr, uid, [invoice.id],
                                               #~ "account.invoice.facturae.webkit",
                                               #~ fname)

            report_multicompany_obj = self.pool.get('report.multicompany')
            report_ids = report_multicompany_obj.search(
                cr, uid, [('model', '=', 'account.invoice')], limit=1) or False
            report_name = "account.invoice.facturae.webkit" 
            if report_ids:
                report_name = report_multicompany_obj.browse(cr, uid, report_ids[0]).report_name
            service = netsvc.LocalService("report."+report_name)
            (result, format) = service.create(cr, SUPERUSER_ID, [invoice.id], report_name, context=context)                
            attachment_ids = attachment_obj.search(cr, uid, [
                ('res_model', '=', 'account.invoice'),
                ('res_id', '=', invoice.id),
                ('datas_fname', '=', invoice.fname_invoice + '.pdf')])
            for attachment in self.browse(cr, uid, attachment_ids, context=context):
                # TODO: aids.append( attachment.id ) but without error in last
                # write
                aids = attachment.id
                attachment_obj.write(cr, uid, [attachment.id], {
                    'name': invoice.fname_invoice + '.pdf', }, context=context)
            if aids:
                msj = _("Attached Successfully PDF\n")
            else:
                raise osv.except_osv(_('Warning'), _('Not Attached PDF\n'))
            self.write(cr, uid, ids, {
                'file_pdf': aids or False,
                'msj': msj,
                'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'file_pdf_index': index_pdf}, context=context)
            wf_service.trg_validate(
                uid, self._name, ids[0], 'action_printable', cr)
            return True
        except Exception, e:
            error = tools.ustr(traceback.format_exc())
            self.write(cr, uid, ids, {'msj': error}, context=context)
            _logger.error(error)
            return False

    def action_printable(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'printable'}, context=context)

    def signal_send_customer(self, cr, uid, ids, context=None):
        try:
            if context is None:
                context = {}
            attachments = []
            msj = ''
            attach_name = ''
            state = ''
            partner_mail = ''
            user_mail = ''
            company_id = self.pool.get('res.users').browse(
                cr, uid, uid, context=context).company_id.id
            invoice = self.browse(cr, uid, ids)[0].invoice_id
            address_id = self.pool.get('res.partner').address_get(
                cr, uid, [invoice.partner_id.id], ['invoice'])['invoice']
            partner_invoice_address = self.pool.get(
                'res.partner').browse(cr, uid, address_id, context=context)
            type = self.browse(cr, uid, ids)[0].type
            wf_service = netsvc.LocalService("workflow")
            fname_invoice = invoice.fname_invoice and invoice.fname_invoice or ''
            adjuntos = self.pool.get('ir.attachment').search(cr, uid, [(
                'res_model', '=', 'account.invoice'), ('res_id', '=', invoice)])
            subject = 'Invoice ' + (invoice.number or '')
            for attach in self.pool.get('ir.attachment').browse(cr, uid, adjuntos):
                attachments.append(attach.id)
                attach_name += attach.name + ', '
            if release.version >= '7':
                obj_ir_mail_server = self.pool.get('ir.mail_server')
                obj_mail_mail = self.pool.get('mail.mail')
                obj_users = self.pool.get('res.users')
                obj_partner = self.pool.get('res.partner')
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
                    mail_compose_message_pool = self.pool.get(
                        'mail.compose.message')
                    email_pool = self.pool.get('email.template')

                    report_multicompany_obj = self.pool.get('report.multicompany')
                    report_ids = report_multicompany_obj.search(
                                    cr, uid, [('model', '=', 'account.invoice')], limit=1) or False
                    if report_ids:
                        report_name = report_multicompany_obj.browse(cr, uid, report_ids[0]).report_name
                        if report_name:
                            tmp_id = email_pool.search(
                                cr, uid, [(
                                    'model_id.model', '=', 'account.invoice'),
                                    ('company_id',
                                     '=', company_id),
                                    ('mail_server_id',
                                     '=', smtp_server.id),
                                    ('report_template.report_name', '=',
                                     report_name)
                                ], limit=1, context=context)
                    else:
                        tmp_id = email_pool.search(
                            cr, uid, [(
                                'model_id.model', '=', 'account.invoice'),
                                ('company_id', '=', company_id),
                                ('mail_server_id', '=', smtp_server.id),
                                ('report_template.report_name', '=',
                                 'account.invoice.facturae.webkit')
                            ], limit=1, context=context)

                    if tmp_id:
                        message = mail_compose_message_pool.onchange_template_id(
                            cr, uid, [], template_id=tmp_id[
                                0], composition_mode=None,
                            model='account.invoice', res_id=invoice.id, context=context)
                        mssg = message.get('value', False)
                        user_mail = obj_users.browse(
                            cr, uid, uid, context=None).email
                        partner_id = mssg.get('partner_ids', False)
                        partner_mail = obj_partner.browse(
                            cr, uid, partner_id)[0].email
                        partner_name = obj_partner.browse(
                            cr, uid, partner_id)[0].name
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
                                    else:
                                        msj = _('Email Send Successfully.Attached is sent to %s for Outgoing Mail Server %s') % (
                                            partner_mail, server_name)
                                        self.write(cr, uid, ids, {
                                            'msj': msj,
                                            'last_date': time.strftime('%Y-%m-%d %H:%M:%S')})
                                        wf_service.trg_validate(
                                            uid, self._name, ids[0], 'action_send_customer', cr)
                                        return True
                            else:
                                raise osv.except_osv(
                                    _('Warning'), _('This user does not have mail'))
                        else:
                            raise osv.except_osv(
                                _('Warning'), _('The customer %s does not have mail') % (partner_name))
                    else:
                        raise osv.except_osv(
                            _('Warning'), _('Check that your template is assigned outgoing mail server named %s.\nAlso the field has report_template = Factura Electronica Report.\nTemplate is associated with the same company') % (server_name))
                else:
                    raise osv.except_osv(_('Warning'), _('Not Found\
                    outgoing mail server.Configure the outgoing mail server named "FacturaE"'))
        except Exception, e:
            error = tools.ustr(traceback.format_exc())
            self.write(cr, uid, ids, {'msj': error}, context=context)
            _logger.error(error)
            return False

    def action_send_customer(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'sent_customer'}, context=context)

    def signal_send_backup(self, cr, uid, ids, context=None):
        try:
            if context is None:
                context = {}
            msj = ''
            wf_service = netsvc.LocalService("workflow")
            msj = _('Send Backup\n')
            self.write(cr, uid, ids, {'msj': msj,
                                      'last_date': time.strftime('%Y-%m-%d %H:%M:%S')
                                      }, context=context)
            wf_service.trg_validate(
                uid, self._name, ids[0], 'action_send_backup', cr)
            return True
        except Exception, e:
            error = tools.ustr(traceback.format_exc())
            self.write(cr, uid, ids, {'msj': error}, context=context)
            _logger.error(error)
            return False

    def action_send_backup(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'sent_backup'}, context=context)

    def signal_done(self, cr, uid, ids, context=None):
        try:
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
        except Exception, e:
            error = tools.ustr(traceback.format_exc())
            self.write(cr, uid, ids, {'msj': error}, context=context)
            _logger.error(error)
            return False

    def action_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)

    def signal_cancel(self, cr, uid, ids, context=None):
        try:
            invoice_obj = self.pool.get('account.invoice')
            attach_obj = self.pool.get('ir.attachment')
            wf_service = netsvc.LocalService("workflow")
            inv_cancel_status = False
            for ir_attach_facturae_mx_id in self.browse(cr, uid, ids, context=context):
                msj = ''
                invoice = ir_attach_facturae_mx_id.invoice_id
                if 'cfdi' in ir_attach_facturae_mx_id.type:
                    if not ir_attach_facturae_mx_id.state in ['cancel', 'draft', 'confirmed']:
                        type__fc = self.get_driver_fc_cancel()
                        if ir_attach_facturae_mx_id.type in type__fc.keys():
                            cfdi_cancel = res = type__fc[ir_attach_facturae_mx_id.type](
                                cr, uid, [
                                    ir_attach_facturae_mx_id.id], context=context
                            )
                            msj += tools.ustr(cfdi_cancel.get('message', False))
                            # TODO, validate cfdi_cancel True or False
                            if cfdi_cancel.get('status', True):
                                wf_service.trg_validate(
                                    uid, self._name, ir_attach_facturae_mx_id.id, 'action_cancel', cr)
                                if invoice.state != 'cancel':
                                    inv_cancel_status = invoice_obj.action_cancel(
                                        cr, uid, [invoice.id], context=context)
                                    cr.execute("""UPDATE ir_attachment
                                                SET res_id = Null
                                                WHERE res_id = %s and res_model='account.invoice'""", (invoice.id,))
                                else:
                                    inv_cancel_status = True
                        else:
                            msj += _("Unknow cfdi driver for %s" % (ir_attach_facturae_mx_id.type))
                    else:
                        wf_service.trg_validate(
                            uid, self._name, ir_attach_facturae_mx_id.id, 'action_cancel', cr)
                        if invoice.state != 'cancel':
                            inv_cancel_status = invoice_obj.action_cancel(
                                cr, uid, [invoice.id], context=context)
                            cr.execute("""UPDATE ir_attachment
                                        SET res_id = Null
                                        WHERE res_id = %s and res_model='account.invoice'""", (invoice.id,))
                        else:
                            inv_cancel_status = True
                        msj = 'cancelled'
                elif 'cfd' in ir_attach_facturae_mx_id.type and not 'cfdi' in ir_attach_facturae_mx_id.type:
                    wf_service.trg_validate(
                                    uid, self._name, ir_attach_facturae_mx_id.id, 'action_cancel', cr)
                    inv_cancel_status = invoice_obj.action_cancel(cr, uid, [invoice.id], context=context)
                    msj = 'cancelled'
                    inv_cancel_status = True
                elif 'cbb' in ir_attach_facturae_mx_id.type:
                    wf_service.trg_validate(
                                    uid, self._name, ir_attach_facturae_mx_id.id, 'action_cancel', cr)
                    inv_cancel_status = invoice_obj.action_cancel(cr, uid, [invoice.id], context=context)
                    msj = 'cancelled'
                    inv_cancel_status = True
                else:
                    raise osv.except_osv(_("Type Electronic Invoice Unknow!"), _(
                        "The Type Electronic Invoice:" + (ir_attach_facturae_mx_id.type or '')))
                self.write(cr, uid, ids, {
                           'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                           'msj': msj,
                           })
        except Exception, e:
            error = tools.ustr( traceback.format_exc() )
            self.write(cr, uid, ids, {'msj': error}, context=context)
            _logger.error( error )
            return False
        return inv_cancel_status

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
