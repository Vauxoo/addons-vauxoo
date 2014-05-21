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
import re

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

    def _get_journal(self, cr, uid, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_id = context.get('company_id', user.company_id.id)
        journal_obj = self.pool.get('account.journal')
        domain = [('company_id', '=', company_id)]
        res = journal_obj.search(cr, uid, domain, limit=1)
        return res and res[0] or False

    def _get_currency(self, cr, uid, context=None):
        res = False
        journal_id = self._get_journal(cr, uid, context=context)
        if journal_id:
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
            res = journal.currency and journal.currency.id or journal.company_id.currency_id.id
        return res

    #~ def _deductions(self, cr, uid, ids, name, arg, context=None):
        #~ if context is None:
            #~ context = {}
        #~ res = {}
        #~ for id in ids:
            #~ res.setdefault(id, 0.0)
        #~ deduction = 0
        #~ payroll = self.browse(cr, uid, ids, context=context)[0]
        #~ for line in payroll.input_line_ids:
            #~ if line.salary_rule_id.type_concept == 'deduction':
                #~ deduction += line.amount + line.exempt_amount
            #~ res[id] =  deduction
        #~ return res
#~ 
    #~ def _perceptions(self, cr, uid, ids, name, arg, context=None):
        #~ if context is None:
            #~ context = {}
        #~ res = {}
        #~ for id in ids:
            #~ res.setdefault(id, 0.0)
        #~ deduction = 0
        #~ payroll = self.browse(cr, uid, ids, context=context)[0]
        #~ for line in payroll.input_line_ids:
            #~ if line.salary_rule_id.type_concept == 'perception':
                #~ deduction += line.amount + line.exempt_amount
            #~ res[id] =  deduction
        #~ return res
        
    #~ def _total(self, cr, uid, ids, name, arg, context=None):
        #~ if context is None:
            #~ context = {}
        #~ res = {}
        #~ perception = 0
        #~ deduction = 0
        #~ total = 0
        #~ for id in ids:
            #~ res.setdefault(id, 0.0)
        #~ perception = self._perceptions(cr, uid, ids, name, arg, context=context)
        #~ deduction =  self._deductions(cr, uid, ids, name, arg, context=context)
        #~ total = perception.values()[0] - deduction.values()[0]
        #~ res[id] =  total
        #~ return res

    _columns = {
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft':[('readonly',False)]}),
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
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, 
                readonly=True, states={'draft':[('readonly',False)]}, track_visibility='always',
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
        'partner_id': fields.related('employee_id', 'address_home_id', type='many2one', relation='res.partner', 
                            string='Partner', store=True, readonly=True, help='Partner referenced to employee'),
        'schedule_pay': fields.related('contract_id', 'schedule_pay', type='selection', selection=([
            ('monthly', _('Monthly')),
            ('quarterly', _('Quarterly')),
            ('semi-annually', _('Semi-annually')),
            ('annually', _('Annually')),
            ('weekly', _('Weekly')),
            ('bi-weekly', _('Bi-weekly')),
            ('bi-monthly', _('Bi-monthly')),
            ]), string="Scheduled Pay", readonly=True),
        'sello': fields.text('Stamp', size=512, help='Digital Stamp'),
        'certificado': fields.text('Certificate', size=64,
            help='Certificate used in the Payroll'),
        'date_payslip_tz': fields.function(_get_date_payslip_tz, method=True,
            type='datetime', string='Date Payroll', store=True,
            help='Date of payroll with Time Zone'),
        #~ 'deduction_total' : fields.function(_deductions, type='float', string='Deductions Total', store=True),
        #~ 'perception_total' : fields.function(_perceptions, type='float', string='Perception Total', store=True),
        #~ 'total' : fields.function(_total, type='float', string='Total', store=True),
    }

    _defaults = {
        'currency_id': _get_currency,
        'journal_id': _get_journal,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.payslip', context=c),
    }

    def _create_original_str(self, cr, uid, ids, invoice_id, context=None):
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
        obj_sequence = self.pool.get('ir.sequence')
        for hr in self.browse(cr, uid, ids, context=context):
            vals_date = self.assigned_datetime(cr, uid,
                {'date_payslip': hr.date_payslip,
                    'payslip_datetime': hr.payslip_datetime},
                    context=context)
            self.write(cr, uid, ids, vals_date, context=context)
            if not hr.line_payslip_product_ids:
                raise osv.except_osv(_('No Product Lines!'), _('Please create some product lines.'))
            super(hr_payslip, self).hr_verify_sheet(cr, uid, ids)
            if hr.journal_id.sequence_id and hr.journal_id.sequence_id.id:
                obj_sequence.next_by_id(cr, uid, hr.journal_id.sequence_id.id, context=context)
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
        attachment_obj = self.pool.get('ir.attachment')
        attach_ids = []
        address_emitter = False
        context_extra_data = {}
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
                    #~ type = payroll.journal_id and payroll.journal_id.sequence_id and \
                            #~ payroll.journal_id.sequence_id.approval_ids[0] and \
                                        #~ payroll.journal_id.sequence_id.approval_ids[0].res_pac.name_driver
                    xml_fname, xml_data = self._get_facturae_payroll_xml_data(cr, uid, ids, context=context)
                    fname = str(payroll.id) + '_XML_V3_2.xml' or ''
                    attachment_id = attachment_obj.create(cr, uid, {
                                        'name': fname,
                                        'datas': base64.encodestring(xml_data),
                                        'datas_fname': fname,
                                        'res_model': self._name,
                                        #~ 'res_id': payroll.id
                                }, context=context)
                    if payroll.company_emitter_id.address_invoice_parent_company_id.use_parent_address:
                        address_emitter = payroll.company_emitter_id.address_invoice_parent_company_id.parent_id
                    else:
                        address_emitter = payroll.company_emitter_id.address_invoice_parent_company_id
                    if address_emitter:
                        context_extra_data.update({'emisor':{'phone':address_emitter.phone,'fax':address_emitter.fax,'mobile':address_emitter.mobile,'web':address_emitter.website,'email':address_emitter.email}})
                    context_extra_data.update({'receptor':{'phone':payroll.partner_id.phone,'fax':payroll.partner_id.fax,'mobile':payroll.partner_id.mobile}})
                    context_extra_data.update({'type': 'payroll'})
                    attach_ids.append( ir_attach_obj.create(cr, uid, {
                        'name': payroll.number or '/',
                        #~ 'type': type,
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
                        #~'file_input_index': base64.encodestring(xml_data),
                        'document_source': payroll.number,
                        'file_input': attachment_id,
                        'context_extra_data': context_extra_data,
                        'res_pac': approval_id.res_pac.id or False,
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
    
    _structure = r"(?P<code>[\d]{3,10})" \
            r"[ \-_]?" \
            r"(?P<pd>[p,P,d,D])" \
            r"[ \-_]?" \
            r"(?P<eg>[e,E,g,G])$"
            
    def get_lines_amount_exemptamount_dict(self, cr, uid, ids, lines, type_line):
        lines_get = {}
        __check_payslip_code_mx_re = re.compile( self._structure )
        for line in lines:
            code_sat = line.code
            m = __check_payslip_code_mx_re.match( code_sat )
            if m:
                code = m.group('code')
                pd = m.group('pd')
                eg = m.group('eg')
                if pd.upper() == type_line:
                    if not lines_get.has_key(code):
                        lines_get.update({code:{'amount':0, 'exempt_amount':0 }})
                    if eg.lower() == 'e':
                        lines_get[code].update({'exempt_amount': abs(line.amount) })
                    elif eg.lower() == 'g':
                        lines_get[code].update({'amount': abs(line.amount) })
        return lines_get
            
    def get_input_line_ids_type(self, cr, uid, ids, lines, type_line, type_amount=False):
        lines_get = []
        deduction = False
        perception = False
        __check_payslip_code_mx_re = re.compile( self._structure )
        for line in lines:
            code_sat = line.code
            m = __check_payslip_code_mx_re.match( code_sat )
            if m:
                code = m.group('code')
                pd = m.group('pd')
                eg = m.group('eg')
                if line.amount <> 0 and pd=="P":
                    perception = True
                if abs(line.amount) <> 0 and pd=="D":
                    deduction = True
                if type_amount:
                    if pd.upper() == type_line:
                        if eg.upper() == type_amount:
                            lines_get.append(line)
                else:
                    if pd.upper() == type_line:
                        lines_get.append(line)
        if not perception:
            raise osv.except_osv(_('Warning !'), _('At least there must be a perception'))
        if not deduction:
            raise osv.except_osv(_('Warning !'), _('At least there must be a deduction'))
        return lines_get
        
    def get_line_short_type(self, cr, uid, ids, lines, type_line):
        lines_get = []
        lines_code = []
        lines_type = []
        __check_payslip_code_mx_re = re.compile( self._structure )
        for line in lines:
            code_sat = line.code
            m = __check_payslip_code_mx_re.match( code_sat )
            if m:
                code = m.group('code')
                pd = m.group('pd')
                if pd.upper() == type_line:
                        lines_code.append(code)
                        lines_type.append(line)
        lines_code = list(set(lines_code))
        #~ import pdb;pdb.set_trace()
        for line in lines_type:
            code_sat = line.code
            m = __check_payslip_code_mx_re.match( code_sat )
            if m:
                code = m.group('code')
                if code in lines_code:
                    lines_get.append(line)
                    lines_code.remove(code)
        #~ import pdb;pdb.set_trace()
        return lines_get

    def onchange_journal_id(self, cr, uid, ids, journal_id, context=None):
        if context is None:
            context = {}
        folio_data = {}
        approval_id = False
        currency_id = False
        company_id = False
        id = ids and ids[0] or False
        if journal_id:
            journal_id = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
            #~ sequence_id = self._get_invoice_sequence(cr, uid, [id])[id]
            currency_id = journal_id.currency and journal_id.currency.id or journal_id.company_id.currency_id.id
            company_id = journal_id.company_id.id
            sequence_id = journal_id and journal_id.sequence_id and journal_id.sequence_id.id or False
            if sequence_id:
                #~ # NO ES COMPATIBLE CON TINYERP approval_id =
                #~ # sequence.approval_id.id
                approval_id = self.pool.get('ir.sequence')._get_current_approval(
                    cr, uid, [sequence_id], field_names=None, arg=False,
                    context=context)[sequence_id]
        result = {'value' : {
                'approval_id' : approval_id, 
                'currency_id': currency_id,
                'company_id': company_id
                }
            }
        return result

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
        
    def _get_taxes(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        importe = 0.0
        tasa = 0.0
        impuesto=''
        ids = isinstance(ids, (int, long)) and [ids] or ids
        payroll = self.browse(cr, uid, ids)[0]
        totalImpuestosTrasladados = 0.0
        tax_requireds = ['IVA', 'IEPS']
        payroll_data_parent = {}
        payroll_data = payroll_data_parent = {}
        payroll_data['Impuestos'] = {}
        payroll_data_impuestos = payroll_data['Impuestos']
        payroll_data_impuestos['Traslados'] = []
        payroll_data_impuestos['Retenciones'] = []
        totalImpuestosTrasladados = 0
        totalImpuestosRetenidos = 0
        isr_amount = 0
        iva_amount = 0
        isr_found = False
        for line in payroll.line_ids:
            rule = line.name.upper()
            if rule == 'ISR':
                isr_amount += line.amount
                isr_found = True
            elif rule == 'IVA':
                iva_amount = line.amount
                payroll_data_impuestos['Retenciones'].append({'Retencion': {
                            'impuesto': 'IVA',
                            'importe': "%.2f" % (iva_amount),
                        }})
        payroll_data['Impuestos'].update({
            'totalImpuestosRetenidos': "%.2f"%( (iva_amount + abs(isr_amount)) or 0.0 )
        })
        if isr_found:
            payroll_data_impuestos['Retenciones'].append({'Retencion': {
                            'impuesto': 'ISR',
                            'importe': "%.2f" % (abs(isr_amount)),
                        }})
        tax_requireds = ['IVA', 'IEPS']
        for tax_required in tax_requireds:
            payroll_data_impuestos['Traslados'].append({'Traslado': {
                'impuesto': self.string_to_xml_format(cr, uid, ids, tax_required),
                'tasa': "%.2f" % (0.0),
                'importe': "%.2f" % (0.0),
            }})
        payroll_data['Impuestos'].update({
            'totalImpuestosTrasladados': "%.2f"%( iva_amount or 0.0),
        })
        return payroll_data_impuestos

    def _get_descuento(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        payroll = self.browse(cr, uid, ids)[0]
        discount = 0
        for line in payroll.line_ids:
            rule = line.name.upper()
            if line.amount < 0:
                if not rule == 'ISR':
                    discount += line.amount
        return abs(discount)

    def _get_facturae_payroll_xml_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        contract_obj = self.pool.get('hr.contract')
        ids = isinstance(ids, (int, long)) and [ids] or ids
        payroll = self.browse(cr, uid, ids)[0]
        if payroll:
            payroll_version = '11'
            payroll_type='nomina'
            context.update(self._get_file_globals(cr, uid, ids, context=context))
            cert_str = self._get_certificate_str(context['fname_cer'])
            cert_str = cert_str.replace('\n\r', '').replace('\r\n', '').replace('\n', '').replace('\r', '').replace(' ', '')
            noCertificado = self._get_noCertificado(cr, uid, ids, context['fname_cer'])
            all_paths = tools.config["addons_path"].split(",")
            formaDePago = payroll.string_to_xml_format(u'Pago en una sola exhibicion')
            data_taxes = self._get_taxes(cr, uid, ids, context=None)
            for my_path in all_paths:
                if os.path.isdir(os.path.join(my_path, 'l10n_mx_payroll_base', 'template')):
                    fname_jinja_tmpl = my_path and os.path.join(my_path, 'l10n_mx_payroll_base', 'template', 'cfdi' + '.xml') or ''
            dictargs2 = {
                'o': payroll,
                'time': ti,
                'employee': payroll.employee_id,
                'noCertificado': noCertificado,
                'formaDePago': formaDePago,
                'certificado': cert_str,
                'fecha': ti.strftime('%Y-%m-%dT%H:%M:%S', ti.strptime(str(payroll.date_payslip_tz), '%Y-%m-%d %H:%M:%S')) ,
                'data_taxes':data_taxes,
                }
            context.update({'fecha': ti.strftime('%Y-%m-%dT%H:%M:%S', ti.strptime(str(payroll.date_payslip_tz), '%Y-%m-%d %H:%M:%S')) or ''})
            (fileno_xml, fname_xml) = tempfile.mkstemp('.xml', 'openerp_' + '__facturae__')
            if fname_jinja_tmpl:
                with open(fname_jinja_tmpl, 'r') as f_jinja_tmpl:
                    jinja_tmpl_str = f_jinja_tmpl.read()
                    tmpl = jinja2.Template( jinja_tmpl_str )
                    with open(fname_xml, 'w') as new_xml:
                        new_xml.write( tmpl.render(**dictargs2) )
            with open(fname_xml,'rb') as b:
                data_xml = b.read()
            b.close()
            for my_path in all_paths:
                if os.path.isdir(os.path.join(my_path, 'l10n_mx_payroll_base', 'template')):
                    fname_jinja_tmpl = my_path and os.path.join(my_path, 'l10n_mx_payroll_base', 'template', 'nomina11' + '.xml') or ''
            context.update({'lang' : self.pool.get('res.users').browse(cr, uid, uid, context=context).lang})
            schedule_pay_values = contract_obj.fields_get(cr, uid, 'schedule_pay', context=context).get('schedule_pay').get('selection')
            schedule_pay_values_dict = {lin[0]: lin[1] for lin in schedule_pay_values}
            dictargs = {
                'a': payroll,
                'schedule_pay': schedule_pay_values_dict,
                'employee': payroll.employee_id,
                'time': ti,
                're': re,
                'abs': abs,
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
                data_xml_payroll = b.read()
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
            doc_xml_full = doc_xml_full.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>')
            doc_xml_full = doc_xml_full.replace('<?xml version="1.0" encoding="UTF-8"?>', '<?xml version="1.0" encoding="UTF-8"?>\n')
        return fname_xml, doc_xml_full

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
            'currency_id': self._get_currency(cr, uid, context=context),
        })
        return super(hr_payslip, self).copy(cr, uid, id, default, context=context)
