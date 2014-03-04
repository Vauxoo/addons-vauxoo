#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: vauxoo consultores (info@vauxoo.com)
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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import pooler, tools, netsvc
import xml
import codecs
import datetime
from datetime import *
import pytz
from pytz import timezone
import os
import tempfile
import jinja2
import base64
import cgi
import urllib
from markupsafe import Markup
import time as ti

from openerp import release

try:
    from qrcode import *
except:
    _logger.error('Execute "sudo pip install pil qrcode" to use l10n_mx_facturae_pac_finkok module.')


class hr_payslip_product_line(osv.Model):
    
    _name = 'hr.payslip.product.line'

    _columns = {
        'payslip_id': fields.many2one('hr.payslip'),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'amount': fields.float('Amount'),
        
    }

class hr_payslip(osv.Model):

    def string_to_xml_format(self, cr, uid, ids, text):
        #~ return text.encode('utf-8', 'xmlcharrefreplace')
        if text:
            return cgi.escape(text, True).encode('ascii', 'xmlcharrefreplace').replace('\n\n', ' ')

    _inherit = 'hr.payslip'

    def _get_company_emitter_payroll(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        journal_obj = self.pool.get('account.journal')
        for id_ in ids:
            data = self.browse(cr, uid, id_, context=context)
            journal_id = data.journal_id.id
            data_journal = journal_obj.browse(
                cr, uid, journal_id, context=context)
            company_payroll = data_journal.company2_id and \
                data_journal.company2_id.id or data.company_id and \
                data.company_id.id or False
            res[data.id] = company_payroll
        return res

    def _get_address_issued_payroll(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        journal_obj = self.pool.get('account.journal')
        for id_ in ids:
            data = self.browse(cr, uid, id_, context=context)
            journal_id = data.journal_id.id
            data_journal = journal_obj.browse(
                cr, uid, journal_id, context=context)
            a = data_journal.address_invoice_company_id and \
                data_journal.address_invoice_company_id.id or False
            b = data_journal.company2_id and \
            data_journal.company2_id.address_invoice_parent_company_id and \
            data_journal.company2_id.address_invoice_parent_company_id.id or False
            c = data.company_id and \
            data.company_id.address_invoice_parent_company_id and \
            data.company_id.address_invoice_parent_company_id.id or False
            address_payroll = a or b or c or False
            res[data.id] = address_payroll
        return res
        
    def _get_date_payslip_tz(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if context is None:
            context = {}
        res = {}
        if release.version >= '6':
            dt_format = tools.DEFAULT_SERVER_DATETIME_FORMAT
            tz = context.get('tz_invoice_mx', 'America/Mexico_City')
            for payroll in self.browse(cr, uid, ids, context=context):
                res[payroll.id] = payroll.payslip_datetime and tools.\
                    server_to_local_timestamp(payroll.payslip_datetime,
                    tools.DEFAULT_SERVER_DATETIME_FORMAT,
                    tools.DEFAULT_SERVER_DATETIME_FORMAT, context.get(
                    'tz_invoice_mx', 'America/Mexico_City')) or False
        elif release.version < '6':
            # TODO: tz change for openerp5
            for payroll in self.browse(cr, uid, ids, context=context):
                res[payroll.id] = payroll.date_payslip
        return res
        
    def assigned_datetime(self, cr, uid, values, context=None):
        if context is None:
            context = {}
        res = {}
        if values.get('date_payslip', False) and\
                                    not values.get('payslip_datetime', False):
                                    
            user_hour = self._get_time_zone(cr, uid, [], context=context)
            time_payslip = time(abs(user_hour), 0, 0)

            date_payslip = datetime.strptime(values['date_payslip'], '%Y-%m-%d').date()
                
            dt_payslip = datetime.combine(date_payslip, time_payslip).strftime('%Y-%m-%d %H:%M:%S')

            res['payslip_datetime'] = dt_payslip
            res['date_payslip'] = values['date_payslip']
            
        if values.get('payslip_datetime', False) and not\
            values.get('date_payslip', False):
            date_payslip = fields.datetime.context_timestamp(cr, uid,
                datetime.datetime.strptime(values['payslip_datetime'],
                tools.DEFAULT_SERVER_DATETIME_FORMAT), context=context)
            res['date_payslip'] = date_payslip
            res['payslip_datetime'] = values['payslip_datetime']
        
        if 'payslip_datetime' in values  and 'date_payslip' in values:
            if values['payslip_datetime'] and values['date_payslip']:
                date_payslip = datetime.strptime(
                    values['payslip_datetime'],
                    '%Y-%m-%d %H:%M:%S').date().strftime('%Y-%m-%d')
                if date_payslip != values['date_payslip']:
                    raise osv.except_osv(_('Warning!'),
                            _('Payslip dates should be equal'))
                            
        if  not values.get('payslip_datetime', False) and\
                                        not values.get('date_payslip', False):
            res['date_payslip'] = fields.date.context_today(self,cr,uid,context=context)
            res['payslip_datetime'] = fields.datetime.now()
            
        return res

    _columns = {
        'journal_id': fields.many2one('account.journal','Journal', required=True),
        'date_payslip': fields.date('Payslip Date'),
        'payslip_datetime': fields.datetime('Electronic Payslip Date'),
        'line_payslip_product_ids': fields.one2many('hr.payslip.product.line', 'payslip_id', 'Generic Product', required=True),
        'pay_method_id': fields.many2one('pay.method', 'Payment Method',
            readonly=True, states={'draft': [('readonly', False)]}),
        'company_emitter_id': fields.function(_get_company_emitter_payroll,
            type="many2one", relation='res.company', string='Company Emitter \
            Payroll', help='This company will be used as emitter company in \
            the electronic payroll'),
        'address_issued_id': fields.function(_get_address_issued_payroll,
            type="many2one", relation='res.partner', string='Address Issued \
            payroll', help='This address will be used as address that issued \
            for electronic payroll'),
        'currency_id': fields.many2one('res.currency', 'Currency',
            required=False, readonly=True, states={'draft':[('readonly',False)]},
            change_default=True, help='Currency used in the payroll'),
        'approval_id' : fields.many2one('ir.sequence.approval', 'Approval'),
        'cfdi_cbb': fields.binary('CFD-I CBB'),
        'cfdi_sello': fields.text('CFD-I Sello', help='Sign assigned by the SAT'),
        'cfdi_no_certificado': fields.char('CFD-I Certificado', size=32,
                                           help='Serial Number of the Certificate'),
        'cfdi_cadena_original': fields.text('CFD-I Cadena Original',
                                            help='Original String used in the electronic payroll'),
        'cfdi_fecha_timbrado': fields.datetime('CFD-I Fecha Timbrado',
                                               help='Date when is stamped the electronic payroll'),
        'cfdi_folio_fiscal': fields.char('CFD-I Folio Fiscal', size=64,
                                         help='Folio used in the electronic payroll'),
        'date_payslip_cancel': fields.datetime('Date Payroll Cancelled',
            readonly=True, help='If the payroll is cancelled, save the date when was cancel'),
        'pac_id': fields.many2one('params.pac', 'Pac', help='Pac used in singned of the payrol'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'sello': fields.text('Stamp', size=512, help='Digital Stamp'),
        'certificado': fields.text('Certificate', size=64,
            help='Certificate used in the Payroll'),
        'date_payslip_tz': fields.function(_get_date_payslip_tz, method=True,
            type='datetime', string='Date Payroll', store=True,
            help='Date of payroll with Time Zone'),
    }

    def _create_original_str(self, cr, uid, ids, payroll_id, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        payroll = self.browse(cr, uid, payroll_id)
        cfdi_folio_fiscal = payroll.cfdi_folio_fiscal or ''
        cfdi_fecha_timbrado = payroll.cfdi_fecha_timbrado or ''
        if cfdi_fecha_timbrado:
            cfdi_fecha_timbrado=ti.strftime('%Y-%m-%dT%H:%M:%S', ti.strptime(cfdi_fecha_timbrado, '%Y-%m-%d %H:%M:%S'))
        sello = payroll.sello or ''
        cfdi_no_certificado = payroll.cfdi_no_certificado or ''
        original_string = '||1.0|'+cfdi_folio_fiscal+'|'+str(cfdi_fecha_timbrado)+'|'+sello+'|'+cfdi_no_certificado+'||'
        return original_string
        

    def _get_time_zone(self, cr, uid, payroll_id, context=None):
        if context is None:
            context = {}
        res_users_obj = self.pool.get('res.users')
        userstz = res_users_obj.browse(cr, uid, [uid])[0].partner_id.tz
        a = 0
        if userstz:
            hours = timezone(userstz)
            fmt = '%Y-%m-%d %H:%M:%S %Z%z'
            now = datetime.now()
            loc_dt = hours.localize(datetime(now.year, now.month, now.day,now.hour, now.minute, now.second))
            timezone_loc = (loc_dt.strftime(fmt))
            diff_timezone_original = timezone_loc[-5:-2]
            timezone_original = int(diff_timezone_original)
            s = str(datetime.now(pytz.timezone(userstz)))
            s = s[-6:-3]
            timezone_present = int(s)*-1
            a = timezone_original + ((
                timezone_present + timezone_original)*-1)
        return a
    

    def hr_verify_sheet(self, cr, uid, ids, context=None):
        for hr in self.browse(cr, uid, ids, context=context):
            vals_date = self.assigned_datetime(cr, uid,
                {'date_payslip': hr.date_payslip,
                    'payslip_datetime': hr.payslip_datetime},
                    context=context)
            self.write(cr, uid, ids, vals_date, context=context)
            if not hr.line_payslip_product_ids:
                raise osv.except_osv(_('No Product Lines!'), _('Please create some product lines.'))
            super(hr_payslip, self).hr_verify_sheet(cr, uid, ids)
            result = self.create_ir_attachment_payroll(cr, uid, ids, context=context)
            return result

    def create_ir_attachment_payroll(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        attach = ''
        wf_service = netsvc.LocalService("workflow")
        ir_attach_obj = self.pool.get('ir.attachment.facturae.mx')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        attach_ids = []
        file_globals = self._get_file_globals(cr, uid, ids, context=context)
        fname_cer_no_pem = file_globals['fname_cer']
        cerCSD = open(fname_cer_no_pem).read().encode('base64') #Mejor forma de hacerlo
        fname_key_no_pem = file_globals['fname_key']
        keyCSD = fname_key_no_pem and base64.encodestring(open(fname_key_no_pem, "r").read()) or ''
        for payroll in self.browse(cr, uid, ids, context=context):
            cert_id = self.pool.get('res.company')._get_current_certificate(
                cr, uid, [payroll.company_emitter_id.id],
                context=context)[payroll.company_emitter_id.id]
            approval_id = payroll.journal_id and payroll.journal_id.sequence_id and \
                payroll.journal_id.sequence_id.approval_ids and \
                        payroll.journal_id.sequence_id.approval_ids[0] or False
            if approval_id:
                if payroll.employee_id.address_home_id:
                    type = payroll.journal_id and payroll.journal_id.sequence_id and \
                            payroll.journal_id.sequence_id.approval_ids[0] and \
                                        payroll.journal_id.sequence_id.approval_ids[0].type
                    xml_fname, xml_data = self._get_facturae_payroll_xml_data(cr, uid, ids, context=context)
                    attach_ids.append( ir_attach_obj.create(cr, uid, {
                        'name': payroll.number or '/',
                        'type': type,
                        'journal_id': payroll.journal_id and payroll.journal_id.id or False,
                        'company_emitter_id': payroll.company_emitter_id.id,
                        'model_source': self._name or '',
                        'id_source': payroll.id,
                        'attachment_email': payroll.employee_id.work_email or payroll.employee_id.address_home_id.email or  '',
                        'certificate_id': cert_id,
                        'certificate_password': file_globals.get('password', ''),
                        'certificate_file': cerCSD or '',
                        'certificate_key_file': keyCSD or '',
                        'user_pac': '',
                        'password_pac': '',
                        'url_webservice_pac': '',
                        'file_input_index': base64.encodestring(xml_data),
                        'document_source': payroll.number,
                            },
                          context=context)
                        )
                    ir_attach_obj.signal_confirm(cr, uid, attach_ids, context=context)
                else:
                    raise orm.except_orm(_('Warning'), _('This employee does not have a home address'))
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
    
    def get_input_line_ids_type(self, cr, uid, ids, lines, type_line):
        lines_get = []
        for line in lines:
            if line.salary_rule_id.type_concept == type_line:
                lines_get.append(line)
        return lines_get

    def onchange_journal_id(self, cr, uid, ids, journal_id, context=None):
        if context is None:
            context = {}
        folio_data = {}
        approval_id = False
        id = ids and ids[0] or False
        if journal_id:
            journal_id = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
            sequence_id = journal_id and journal_id.sequence_id and journal_id.sequence_id.id
            if sequence_id:
                #~ # NO ES COMPATIBLE CON TINYERP approval_id =
                #~ # sequence.approval_id.id
                approval_id = self.pool.get('ir.sequence')._get_current_approval(
                    cr, uid, [sequence_id], field_names=None, arg=False,
                    context=context)[sequence_id]
        return {'value' : {'approval_id' : approval_id}}

    def binary2file(self, cr, uid, ids, binary_data, file_prefix="", file_suffix=""):
        """
        @param binary_data : Field binary with the information of certificate
                of the company
        @param file_prefix : Name to be used for create the file with the
                information of certificate
        @file_suffix : Sufix to be used for the file that create in this function
        """
        (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
        f = open(fname, 'wb')
        f.write(base64.decodestring(binary_data))
        f.close()
        os.close(fileno)
        return fname

    def _get_file_globals(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        id = ids and ids[0] or False
        file_globals = {}
        
        if id:
            payslip = self.browse(cr, uid, id, context=context)
            now = ti.strftime('%Y-%m-%d %H:%M:%S')
            certificate_id = self.pool.get('res.company')._get_current_certificate(
                cr, uid, [payslip.company_emitter_id.id],
                context=context)[payslip.company_emitter_id.id]
            certificate_id = certificate_id and self.pool.get(
                'res.company.facturae.certificate').browse(
                cr, uid, [certificate_id], context=None)[0] or False

            if certificate_id:
                if not certificate_id.certificate_file_pem:
                    # generate certificate_id.certificate_file_pem, a partir
                    # del certificate_id.certificate_file
                    pass
                fname_cer_pem = False
                try:
                    fname_cer_pem = self.binary2file(cr, uid, ids,
                        certificate_id.certificate_file_pem, 'openerp_' + (
                        certificate_id.serial_number or '') + '__certificate__',
                        '.cer.pem')
                except:
                    raise osv.except_osv(_('Error !'), _(
                        'Not captured a CERTIFICATE file in format PEM, in \
                        the company!'))
                file_globals['fname_cer'] = fname_cer_pem

                fname_key_pem = False
                try:
                    fname_key_pem = self.binary2file(cr, uid, ids,
                        certificate_id.certificate_key_file_pem, 'openerp_' + (
                        certificate_id.serial_number or '') + '__certificate__',
                        '.key.pem')
                except:
                    raise osv.except_osv(_('Error !'), _(
                        'Not captured a KEY file in format PEM, in the company!'))
                file_globals['fname_key'] = fname_key_pem

                fname_cer_no_pem = False
                try:
                    fname_cer_no_pem = self.binary2file(cr, uid, ids,
                        certificate_id.certificate_file, 'openerp_' + (
                        certificate_id.serial_number or '') + '__certificate__',
                        '.cer')
                except:
                    pass
                file_globals['fname_cer_no_pem'] = fname_cer_no_pem

                fname_key_no_pem = False
                try:
                    fname_key_no_pem = self.binary2file(cr, uid, ids,
                        certificate_id.certificate_key_file, 'openerp_' + (
                        certificate_id.serial_number or '') + '__certificate__',
                        '.key')
                except:
                    pass
                file_globals['fname_key_no_pem'] = fname_key_no_pem

                file_globals['password'] = certificate_id.certificate_password

                if certificate_id.fname_xslt:
                    if (certificate_id.fname_xslt[0] == os.sep or \
                        certificate_id.fname_xslt[1] == ':'):
                        file_globals['fname_xslt'] = certificate_id.fname_xslt
                    else:
                        file_globals['fname_xslt'] = os.path.join(
                            tools.config["root_path"], certificate_id.fname_xslt)
                else:
                    # Search char "," for addons_path, now is multi-path
                    all_paths = tools.config["addons_path"].split(",")
                    for my_path in all_paths:
                        if os.path.isdir(os.path.join(my_path,
                            'l10n_mx_facturae_base', 'SAT')):
                            # If dir is in path, save it on real_path
                            file_globals['fname_xslt'] = my_path and os.path.join(
                                my_path, 'l10n_mx_facturae_base', 'SAT',
                                'cadenaoriginal_2_0_l.xslt') or ''
                            break
                if not file_globals.get('fname_xslt', False):
                    raise osv.except_osv(_('Warning !'), _(
                        'Not defined fname_xslt. !'))

                if not os.path.isfile(file_globals.get('fname_xslt', ' ')):
                    raise osv.except_osv(_('Warning !'), _(
                        'No exist file [%s]. !') % (file_globals.get('fname_xslt', ' ')))

                file_globals['serial_number'] = certificate_id.serial_number
            else:
                raise osv.except_osv(_('Warning !'), _(
                    'Check date of payroll and the validity of certificate, & that the register of the certificate is active.\n!') )
            for my_path in all_paths:
                if os.path.isdir(os.path.join(my_path, 'l10n_mx_facturae_base', 'SAT')):
                    # If dir is in path, save it on real_path
                    file_globals['fname_xslt'] = my_path and os.path.join(
                        my_path, 'l10n_mx_facturae_base', 'SAT','cadenaoriginal_3_2',
                        'cadenaoriginal_3_2_l.xslt') or ''
        return file_globals

    def _get_noCertificado(self, cr, uid, ids, fname_cer, pem=True):
        """
        @param fname_cer : Path more name of file created whit information 
                    of certificate with suffix .pem
        @param pem : Boolean that indicate if file is .pem
        """
        certificate_lib = self.pool.get('facturae.certificate.library')
        fname_serial = certificate_lib.b64str_to_tempfile(cr, uid, ids, base64.encodestring(
            ''), file_suffix='.txt', file_prefix='openerp__' + (False or '') + \
            '__serial__')
        result = certificate_lib._get_param_serial(cr, uid, ids,
            fname_cer, fname_out=fname_serial, type='PEM')
        return result

    def _get_sello(self, cr=False, uid=False, ids=False, context=None):
        # TODO: Put encrypt date dynamic
        if context is None:
            context = {}
        fecha = context['fecha']
        year = float(ti.strftime('%Y', ti.strptime(
            fecha, '%Y-%m-%dT%H:%M:%S')))
        if year >= 2011:
            encrypt = "sha1"
        if year <= 2010:
            encrypt = "md5"
        certificate_lib = self.pool.get('facturae.certificate.library')
        fname_sign = certificate_lib.b64str_to_tempfile(cr, uid, ids, base64.encodestring(
            ''), file_suffix='.txt', file_prefix='openerp__' + (False or '') + \
            '__sign__')
        result = certificate_lib._sign(cr, uid, ids, fname=context['fname_xml'],
            fname_xslt=context['fname_xslt'], fname_key=context['fname_key'],
            fname_out=fname_sign, encrypt=encrypt, type_key='PEM')
        
        return result

    def _get_certificate_str(self, fname_cer_pem=""):
        """
        @param fname_cer_pem : Path and name the file .pem
        """
        fcer = open(fname_cer_pem, "r")
        lines = fcer.readlines()
        fcer.close()
        cer_str = ""
        loading = False
        for line in lines:
            if 'END CERTIFICATE' in line:
                loading = False
            if loading:
                cer_str += line
            if 'BEGIN CERTIFICATE' in line:
                loading = True
        return cer_str

    def validate_scheme_facturae_xml(self, cr, uid, ids, datas_xmls=[], facturae_version = None, facturae_type="cfdv", scheme_type='xsd'):
    #TODO: bzr add to file fname_schema
        if not datas_xmls:
            datas_xmls = []
        certificate_lib = self.pool.get('facturae.certificate.library')
        for data_xml in datas_xmls:
            (fileno_data_xml, fname_data_xml) = tempfile.mkstemp('.xml', 'openerp_' + (False or '') + '__facturae__' )
            f = open(fname_data_xml, 'wb')
            f.write( data_xml )
            f.close()
            os.close(fileno_data_xml)
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(os.path.join(my_path, 'l10n_mx_facturae_base', 'SAT')):
                    # If dir is in path, save it on real_path
                    fname_scheme = my_path and os.path.join(my_path, 'l10n_mx_facturae_base', 'SAT', facturae_type + facturae_version +  '.' + scheme_type) or ''
                    #fname_scheme = os.path.join(tools.config["addons_path"], u'l10n_mx_facturae_base', u'SAT', facturae_type + facturae_version +  '.' + scheme_type )
                    fname_out = certificate_lib.b64str_to_tempfile(cr, uid, ids, base64.encodestring(''), file_suffix='.txt', file_prefix='openerp__' + (False or '') + '__schema_validation_result__' )
                    result = certificate_lib.check_xml_scheme(cr, uid, ids, fname_data_xml, fname_scheme, fname_out)
                    if result: #Valida el xml mediante el archivo xsd
                        raise osv.except_osv('Error al validar la estructura del xml!', 'Validación de XML versión %s:\n%s'%(facturae_version, result))
        return True

    def _get_facturae_payroll_xml_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        payroll = self.browse(cr, uid, ids)[0]
        if payroll:
            facturae_version = '11'
            facturae_type='nomina'
            context.update(self._get_file_globals(cr, uid, ids, context=context))
            cert_str = self._get_certificate_str(context['fname_cer'])
            cert_str = cert_str.replace('\n\r', '').replace('\r\n', '').replace('\n', '').replace('\r', '').replace(' ', '')
            noCertificado = self._get_noCertificado(cr, uid, ids, context['fname_cer'])
            all_paths = tools.config["addons_path"].split(",")
            formaDePago = payroll.string_to_xml_format(u'Pago en una sola exhibicion')
            for my_path in all_paths:
                if os.path.isdir(os.path.join(my_path, 'l10n_mx_payroll_base', 'template')):
                    fname_jinja_tmpl = my_path and os.path.join(my_path, 'l10n_mx_payroll_base', 'template', 'cfdi' + '.xml') or ''
            dictargs2 = {
                'a': payroll,
                'time': ti,
                'employee': payroll.employee_id,
                'noCertificado': noCertificado,
                'formaDePago': formaDePago,
                'certificado': cert_str,
                'fecha': ti.strftime('%Y-%m-%dT%H:%M:%S', ti.strptime(str(payroll.date_payslip_tz), '%Y-%m-%d %H:%M:%S')) ,
                }
            context.update({'fecha': ti.strftime('%Y-%m-%dT%H:%M:%S', ti.strptime(str(payroll.date_payslip_tz), '%Y-%m-%d %H:%M:%S')) or ''})
            (fileno_xml, fname_xml) = tempfile.mkstemp('.xml', 'openerp_' + '__facturae__')
            if fname_jinja_tmpl:
                with open(fname_jinja_tmpl, 'r') as f_jinja_tmpl:
                    jinja_tmpl_str = f_jinja_tmpl.read().encode('utf-8')
                    tmpl = jinja2.Template( jinja_tmpl_str )
                    with open(fname_xml, 'w') as new_xml:
                        new_xml.write( tmpl.render(**dictargs2) )
            with open(fname_xml,'rb') as b:
                data_xml = b.read().encode('utf-8')
            b.close()
            if not noCertificado:
                raise osv.except_osv(_('Error in No. Certificate !'), _(
                    "Can't get the Certificate Number of the voucher.\nCkeck your configuration.\n%s") % (msg2))
            fname_txt = fname_xml + '.txt'
            (fileno_sign, fname_sign) = tempfile.mkstemp('.txt', 'openerp_' + '__facturae_txt_md5__')
            os.close(fileno_sign)
            
            try:
                self.validate_scheme_facturae_xml(cr, uid, ids, [data_xml], 'v3.2', 'cfd')
            except Exception, e:
                raise orm.except_orm(_('Warning'), _('Parse Error XML: %s.') % (tools.ustr(e)))
            for my_path in all_paths:
                if os.path.isdir(os.path.join(my_path, 'l10n_mx_payroll_base', 'template')):
                    fname_jinja_tmpl = my_path and os.path.join(my_path, 'l10n_mx_payroll_base', 'template', 'nomina11' + '.xml') or ''
            dictargs = {
                'a': payroll,
                'employee': payroll.employee_id,
                'time': ti,
                }
            payroll2 = "payroll"
            (fileno_xml, fname_xml_payroll) = tempfile.mkstemp('.xml', 'openerp_' + (payroll2 or '') + '__facturae__')
            if fname_jinja_tmpl:
                with open(fname_jinja_tmpl, 'r') as f_jinja_tmpl:
                    jinja_tmpl_str = f_jinja_tmpl.read()
                    tmpl = jinja2.Template( jinja_tmpl_str )
                    with open(fname_xml_payroll, 'w') as new_xml:
                        new_xml.write( tmpl.render(**dictargs) )
            with open(fname_xml_payroll,'rb') as b:
                data_xml_payroll = b.read().encode('UTF-8')
            try:
                self.validate_scheme_facturae_xml(cr, uid, ids, [data_xml_payroll], facturae_version, facturae_type)
            except Exception, e:
                raise orm.except_orm(_('Warning'), _('Parse Error XML: %s.') % (tools.ustr(e)))
            #Agregar nodo Nomina en nodo Complemento
            doc_xml = xml.dom.minidom.parseString(data_xml)
            doc_xml_payroll_2 = xml.dom.minidom.parseString(data_xml_payroll)
            complemento = """<cfdi:Complemento xmlns:cfdi="http://www.sat.gob.mx/cfd/3"></cfdi:Complemento>"""
            cfdi_complemento = xml.dom.minidom.parseString(complemento)
            complemento = cfdi_complemento.documentElement
            nomina = doc_xml_payroll_2.getElementsByTagName('nomina:Nomina')[0]
            complemento.appendChild(nomina)
            #Agregar nodo nodo Complemento en nodo Comprobante
            node_comprobante = doc_xml.getElementsByTagName('cfdi:Comprobante')[0]
            node_comprobante.appendChild(complemento)
            
            doc_xml_full = doc_xml.toxml().encode('ascii', 'xmlcharrefreplace')
            data_xml2 = xml.dom.minidom.parseString(doc_xml_full)
            #~data_xml3 = data_xml2.toxml('UTF-8')
            f = codecs.open(fname_xml,'w','utf-8')
            data_xml2.writexml(f, indent='    ', addindent='    ', newl='\r\n', encoding='UTF-8')
            f.close()
            context.update({
                'fname_xml': fname_xml,
                'fname_txt': fname_txt,
                'fname_sign': fname_sign,
            })
            #context.update({'fecha': date_now or ''})
            sign_str = self._get_sello(cr=False, uid=False, ids=False, context=context)
            nodeComprobante = data_xml2.getElementsByTagName("cfdi:Comprobante")[0]
            nodeComprobante.setAttribute("sello", sign_str)
            data_xml = data_xml2.toxml('UTF-8')
            #~data_xml = codecs.BOM_UTF8 + data_xml
            data_xml = data_xml.replace('<?xml version="1.0" encoding="UTF-8"?>', '<?xml version="1.0" encoding="UTF-8"?>\n')
        return fname_xml, data_xml

    def copy(self, cr, uid, id, default={}, context=None):
        if context is None:
            context = {}
        default.update({
            'date_payslip': False,
            'payslip_datetime': False,
            'cfdi_sello': False,
            'cfdi_no_certificado': False,
            'cfdi_fecha_timbrado': False,
            'cfdi_folio_fiscal': False,
            'pac_id': False,
        })
        return super(hr_payslip, self).copy(cr, uid, id, default, context=context)
