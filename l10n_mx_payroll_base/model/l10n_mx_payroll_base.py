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
from datetime import datetime, timedelta
import pytz
from pytz import timezone
import time
import os
import tempfile
import jinja2
import base64
import cgi
import urllib
from markupsafe import Markup

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

    def _get_company_emitter_invoice(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        journal_obj = self.pool.get('account.journal')
        for id_ in ids:
            data = self.browse(cr, uid, id_, context=context)
            journal_id = data.journal_id.id
            data_journal = journal_obj.browse(
                cr, uid, journal_id, context=context)
            company_invoice = data_journal.company2_id and \
                data_journal.company2_id.id or data.company_id and \
                data.company_id.id or False
            res[data.id] = company_invoice
        return res

    def _get_address_issued_invoice(self, cr, uid, ids, name, args, context=None):
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
            address_invoice = a or b or c or False
            res[data.id] = address_invoice
        return res

    #~ def _get_date_payslip_tz(self, cr, uid, ids, field_names=None, arg=False, context=None):
        #~ if context is None:
            #~ context = {}
        #~ res = {}
        #~ if release.version >= '6':
            #~ dt_format = tools.DEFAULT_SERVER_DATETIME_FORMAT
            #~ tz = context.get('tz_invoice_mx', 'America/Mexico_City')
            #~ for invoice in self.browse(cr, uid, ids, context=context):
                #~ res[invoice.id] = invoice.payslip_datetime and tools.\
                    #~ server_to_local_timestamp(invoice.payslip_datetime,
                    #~ tools.DEFAULT_SERVER_DATETIME_FORMAT,
                    #~ tools.DEFAULT_SERVER_DATETIME_FORMAT, context.get(
                    #~ 'tz_invoice_mx', 'America/Mexico_City')) or False
        #~ elif release.version < '6':
            #~ # TODO: tz change for openerp5
            #~ for invoice in self.browse(cr, uid, ids, context=context):
                #~ res[invoice.id] = invoice.date_invoice
        #~ return res

    _columns = {
        'journal_id': fields.many2one('account.journal','Journal', required=True),
        'date_payslip': fields.date('Payslip Date'),
        'payslip_datetime': fields.datetime('Electronic Payslip Date'),
        'line_payslip_product_ids': fields.one2many('hr.payslip.product.line', 'payslip_id', 'Generic Product', required=True),
        'pay_method_id': fields.many2one('pay.method', 'Payment Method',
            readonly=True, states={'draft': [('readonly', False)]}),
        'company_emitter_id': fields.function(_get_company_emitter_invoice,
            type="many2one", relation='res.company', string='Company Emitter \
            Payroll', help='This company will be used as emitter company in \
            the electronic payroll'),
        'address_issued_id': fields.function(_get_address_issued_invoice,
            type="many2one", relation='res.partner', string='Address Issued \
            Invoice', help='This address will be used as address that issued \
            for electronic payroll'),
        'currency_id': fields.many2one('res.currency', 'Currency',
            required=False, readonly=True, states={'draft':[('readonly',False)]},
            change_default=True, help='Currency used in the invoice'),
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
        'date_invoice_cancel': fields.datetime('Date Payroll Cancelled',
            readonly=True, help='If the payroll is cancelled, save the date when was cancel'),
        'pac_id': fields.many2one('params.pac', 'Pac', help='Pac used in singned of the payrol'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'sello': fields.text('Stamp', size=512, help='Digital Stamp'),
        'certificado': fields.text('Certificate', size=64,
            help='Certificate used in the Payroll'),
        'date_payslip_tz':  fields.datetime(string='Date Payroll with TZ',
            help='Date of Payroll with Time Zone'),
    }

    def _create_original_str(self, cr, uid, ids, invoice_id, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        invoice = self.browse(cr, uid, invoice_id)
        cfdi_folio_fiscal = invoice.cfdi_folio_fiscal or ''
        cfdi_fecha_timbrado = invoice.cfdi_fecha_timbrado or ''
        if cfdi_fecha_timbrado:
            cfdi_fecha_timbrado=time.strftime('%Y-%m-%dT%H:%M:%S', time.strptime(cfdi_fecha_timbrado, '%Y-%m-%d %H:%M:%S'))
        sello = invoice.sello or ''
        cfdi_no_certificado = invoice.cfdi_no_certificado or ''
        original_string = '||1.0|'+cfdi_folio_fiscal+'|'+str(cfdi_fecha_timbrado)+'|'+sello+'|'+cfdi_no_certificado+'||'
        return original_string

    def hr_verify_sheet(self, cr, uid, ids, context=None):
        for hr in self.browse(cr, uid, ids, context=context):
            if hr.payslip_datetime:
                htz = int(self._get_time_zone(cr, uid, ids, context=context))
                self.write(cr, uid, ids, {'date_payslip_tz' : (datetime.strptime(hr.payslip_datetime, '%Y-%m-%d %H:%M:%S') + timedelta(hours=htz)).strftime('%Y-%m-%d %H:%M:%S'),
                    'date_payslip': (datetime.strptime(hr.payslip_datetime, '%Y-%m-%d').strftime('%Y-%m-%d'))})
            else:
                now = datetime.now()
                htz = int(self._get_time_zone(cr, uid, ids, context=context))
                res = (now).strftime('%Y-%m-%d %H:%M:%S')
                self.write(cr, uid, ids, {'date_payslip_tz' : (now + timedelta(hours=htz)).strftime('%Y-%m-%d %H:%M:%S'), 'payslip_datetime': res,'date_payslip': (now).strftime('%Y-%m-%d')})
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
        for payroll in self.browse(cr, uid, ids, context=context):
            cert_id = self.pool.get('res.company')._get_current_certificate(
                cr, uid, [payroll.company_emitter_id.id],
                context=context)[payroll.company_emitter_id.id]
            approval_id = payroll.journal_id and payroll.journal_id.sequence_id and \
                payroll.journal_id.sequence_id.approval_ids and \
                        payroll.journal_id.sequence_id.approval_ids[0] or False
            if approval_id:
                if payroll.employee_id.address_home_id:
                    try:
                        type = payroll.journal_id and payroll.journal_id.sequence_id and \
                            payroll.journal_id.sequence_id.approval_ids[0] and \
                                        payroll.journal_id.sequence_id.approval_ids[0].type
                    except:
                        raise orm.except_orm(_('Warning'), _('This journal does not have an approval'))
                    attach_ids.append( ir_attach_obj.create(cr, uid, {
                          'name': payroll.number or '/', 'type': type,
                          'journal_id': payroll.journal_id and payroll.journal_id.id or False,
                          'payroll_id': payroll and payroll.id or False,
                          'company_emitter_id': payroll.company_emitter_id.id,
                          'certificate_id': cert_id,
                          'partner_id': payroll.partner_id and payroll.partner_id.id or False},
                          
                          context=None)#Context, because use a variable type of our code but we dont need it.
                        )
                    ir_attach_obj.signal_confirm(cr, uid, attach_ids, context=context)
                else:
                    raise orm.except_orm(_('Warning'), _('This employee does not have a home address'))
            else:
                raise orm.except_orm(_('Warning'), _('This journal does not have an approval'))
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
    
    def get_input_line_ids_type(self, cr, uid, ids, lines, type_line):
        lines_get = []
        for line in lines:
            if line.salary_rule_id.type_concept == type_line:
                lines_get.append(line)
        return lines_get

    #~ def _get_dict_payroll(self, cr, uid, ids, context=None):
        #~ if context is None:
            #~ context = {}
        #~ ids = isinstance(ids, (int, long)) and [ids] or ids
        #~ list_data = []
        #~ department = ''
        #~ for p in self.browse(cr, uid, ids, context=context):
            #~ dict_data = {}
            #~ tipoComprobante = 'egreso'
            #~ # Inicia seccion: Nomina
            #~ htz = int(self._get_time_zone(cr, uid, [p.id], context=context))
            #~ now = time.strftime('%Y-%m-%d %H:%M:%S')
            #~ date_now = now and datetime.strptime(p.payslip_datetime, '%Y-%m-%d %H:%M:%S') + timedelta(hours=htz) or False
            #~ date_now = now
            #~ date_now = time.strftime('%Y-%m-%d', time.strptime(str(date_now), '%Y-%m-%d %H:%M:%S')) or False
            #~ number_of_days=0
            #~ worked_days_line_ids = p.worked_days_line_ids
            #~ if worked_days_line_ids:
                #~ for n in worked_days_line_ids:
                    #~ number_of_days += n['number_of_days']
            #~ if p.employee_id.department_id:
                #~ department = p.employee_id.department_id.name
                #~ department = self.conv_ascii(cr, uid, ids, department)
            #~ dict_data['nomina:Nomina'] = {}
            #~ dict_data['nomina:Nomina'].update({
                #~ 'RegistroPatronal': p.employee_id.employer_registration and \
                #~ p.employee_id.employer_registration.replace('\n\r', ' ').replace(
                    #~ '\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A',
                #~ 'NumEmpleado': p.employee_id.identification_id or 'S/N',
                #~ 'CURP': p.employee_id.curp and \
                            #~ p.employee_id.curp.replace('\n\r', ' ').replace(
                                #~ '\r\n', ' ').replace('\n', ' ').replace('\r', ' ').upper() or 'S/N',
                #~ 'TipoRegimen': p.employee_id.regime_id.code and\
                                   #~ p.employee_id.regime_id.code or '2',
                #~ 'NumSeguridadSocial':p.employee_id.nss and \
                            #~ p.employee_id.nss.replace('\n\r', ' ').replace(
                                #~ '\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'S/N',
                #~ 'FechaPago': date_now or False,
                #~ 'FechaInicialPago': p.date_from or False,
                #~ 'FechaFinalPago': p.date_to or False,
                #~ 'FechaInicioRelLaboral': p.contract_id.date_start and \
                                            #~ p.contract_id.date_start or False,
                #~ 'NumDiasPagados': number_of_days or 0.0,
                #~ 'Departamento': department or 'N/A',
                #~ 'CLABE': p.employee_id.bank_account_id.clabe and \
                        #~ p.employee_id.bank_account_id.clabe.replace('\n\r', ' ').\
                        #~ replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '000000000000000000',
                #~ 'Banco': p.employee_id.bank_account_id.bank and \
                            #~ p.employee_id.bank_account_id.bank.code.replace(
                                #~ '\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace(
                                        #~ '\r', ' ') or '001',
                #~ 'Antiguedad':p.employee_id.seniority or 0,
                #~ 'Puesto': p.employee_id.job_id.name and \
                                #~ p.contract_id.job_id.name or 'N/A',
                #~ 'TipoContrato': p.contract_id.type_id.name or '',
                #~ 'TipoJornada': p.contract_id.working_day_id.name or '',
                #~ 'PeriodicidadPago': p.contract_id.schedule_pay or '',
                #~ 'RiesgoPuesto': p.contract_id.risk_rank_id.code or '1',
                #~ 'SalarioBaseCotApor': p.contract_id.wage or 0,
                #~ 'SalarioDiarioIntegrado': p.contract_id.integrated_salary or 0,
                #~ 'xmlns:nomina':'http://www.sat.gob.mx/nomina',
                #~ 'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                #~ 'Version': '1.1'
            #~ })
            #~ input_line_ids = p.input_line_ids
            #~ if input_line_ids:
                #~ TotalGravado_percepcion = 0
                #~ TotalExento_percepcion = 0
                #~ TotalExento_deduccion = 0
                #~ TotalGravado_deduccion = 0
                #~ lista_percepciones = []
                #~ lista_deducciones = []
                #~ var = 0
                #~ percepciones_data = dict_data['nomina:Nomina']
                #~ percepciones_data['nomina:Percepciones'] = {}
                #~ deducciones_data = dict_data['nomina:Nomina']
                #~ deducciones_data['nomina:Deducciones'] = {}
                #~ for n in input_line_ids:
                    #~ if n['salary_rule_id']['type_concept']=='perception':
                        #~ concepto = self.conv_ascii(cr, uid, ids, n['salary_rule_id']['name'])
                        #~ data_percepciones = {
                                        #~ 'TipoPercepcion': n['salary_rule_id']['code'],
                                        #~ 'Clave': n['salary_rule_id']['code']+'clave',
                                        #~ 'Concepto': concepto or '',
                                        #~ 'ImporteGravado': n['amount'],
                                        #~ 'ImporteExento': n['exempt_amount']
                                        #~ }
                        #~ TotalGravado_percepcion +=  n['amount']
                        #~ TotalExento_percepcion +=  n['exempt_amount']
                        #~ lista_percepciones.append(data_percepciones)
                    #~ if n['salary_rule_id']['type_concept']=='deduction':
                        #~ concepto = self.conv_ascii(cr, uid, ids, n['salary_rule_id']['name'])
                        #~ data_deducciones = {
                                        #~ 'TipoDeduccion': n['salary_rule_id']['code'],
                                        #~ 'Clave': n['salary_rule_id']['clave'] or '',
                                        #~ 'Concepto': concepto or '',
                                        #~ 'ImporteGravado': n['amount'],
                                        #~ 'ImporteExento': n['exempt_amount'],
                                        #~ }
                        #~ TotalGravado_deduccion +=  n['amount']
                        #~ TotalExento_deduccion += n['exempt_amount']
                        #~ lista_deducciones.append(data_deducciones)
                #~ percepciones_data['nomina:Percepciones'].update({
                                            #~ 'TotalGravado': TotalGravado_percepcion,
                                            #~ 'TotalExento': TotalExento_percepcion,
                                            #~ 'nomina:Percepcion' : lista_percepciones,
                                                        #~ })
#~ 
                #~ deducciones_data['nomina:Deducciones'].update({
                                            #~ 'TotalGravado': TotalGravado_deduccion,
                                            #~ 'TotalExento': TotalExento_deduccion,
                                            #~ 'nomina:Deduccion' : lista_deducciones,
                                                        #~ })
            #~ else:
                #~ raise orm.except_orm(_('Warning'), _('The payroll not have deductions or perceptions'))
            #~ inability_line_ids = p.inability_line_ids
            #~ if inability_line_ids:
                #~ lista_incapacidades = []
                #~ descuento = 0
                #~ number_of_days = 0
                #~ incapacidades_data = dict_data['nomina:Nomina']
                #~ incapacidades_data['nomina:Incapacidades'] = {}
                #~ for n in inability_line_ids:
                    #~ descuento += n['amount']
                    #~ number_of_days += n['number_of_days']
                    #~ data_incapacidades = {
                                        #~ 'DiasIncapacidad': n['number_of_days'] or 0,
                                        #~ 'TipoIncapacidad': n['inability_id']['code'] or 1,
                                        #~ 'Descuento': n['amount'] or 0,
                                        #~ }
                    #~ lista_incapacidades.append(data_incapacidades)
                #~ incapacidades_data['nomina:Incapacidades'].update({
                                                    #~ 'nomina:Incapacidad' : lista_incapacidades
                                                            #~ })
            #~ overtime_line_ids = p.overtime_line_ids
            #~ if overtime_line_ids:
                #~ lista_horasextras = []
                #~ ImportePagado = 0
                #~ number_of_days = 0
                #~ number_of_hours = 0
                #~ horasextras_data = dict_data['nomina:Nomina']
                #~ horasextras_data['nomina:HorasExtras'] = {}
                #~ for n in overtime_line_ids:
                    #~ ImportePagado += n['amount']
                    #~ number_of_days += n['number_of_days']
                    #~ number_of_hours += n['number_of_hours']
                    #~ if n['type_hours'] == 'double':
                        #~ TipoHoras = 'Dobles'
                    #~ if n['type_hours'] == 'triples':
                        #~ TipoHoras = 'Triples'
                    #~ data_horasextras = {'Dias': n['number_of_days'] or 0,
                                        #~ 'TipoHoras': TipoHoras,
                                        #~ 'HorasExtra': n['number_of_hours'] or 0,
                                        #~ 'ImportePagado': n['amount'] or 0,
                                        #~ }
                    #~ lista_horasextras.append(data_horasextras)
                #~ horasextras_data['nomina:HorasExtras'].update({
                                            #~ 'nomina:HorasExtra' : lista_horasextras
                                                            #~ })
        #~ list_data.append(dict_data)
        #~ return list_data

    def onchange_journal_id(self, cr, uid, ids, journal_id, context=None):
        if context is None:
            context = {}
        folio_data = {}
        approval_id = False
        id = ids and ids[0] or False
        if journal_id:
            journal_id = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
            #~ sequence_id = self._get_invoice_sequence(cr, uid, [id])[id]
            sequence_id = journal_id and journal_id.sequence_id and journal_id.sequence_id.id
            if sequence_id:
                #~ # NO ES COMPATIBLE CON TINYERP approval_id =
                #~ # sequence.approval_id.id
            #~ number_work = payslip.number or invoice.internal_number
            #~ if invoice.type in ['out_invoice', 'out_refund']:
                #~ try:
                    #~ if number_work:
                        #~ int(number_work)
                #~ except(ValueError):
                    #~ raise osv.except_osv(_('Warning !'), _(
                        #~ 'The folio [%s] must be integer number, without letters')\
                            #~ % (number_work))
            #~ context.update({'number_work': number_work or False})
                approval_id = self.pool.get('ir.sequence')._get_current_approval(
                    cr, uid, [sequence_id], field_names=None, arg=False,
                    context=context)[sequence_id]
            #~ approval = approval_id and self.pool.get(
                #~ 'ir.sequence.approval').browse(cr, uid, [approval_id],
                #~ context=context)[0] or False
            #~ if approval:
                #~ folio_data = {
                    #~ 'serie': approval.serie or '',
                    #~ #'folio': '1',
                    #~ 'noAprobacion': approval.approval_number or '',
                    #~ 'anoAprobacion': approval.approval_year or '',
                    #~ 'desde': approval.number_start or '',
                    #~ 'hasta': approval.number_end or '',
                    #~ #'noCertificado': "30001000000100000800",
                #~ }
            #~ else:
                #~ raise osv.except_osv(_('Warning !'), _(
                    #~ "The sequence don't have data of electronic invoice\nIn the sequence_id [%d].\n %s !")\
                        #~ % (sequence_id, msg2))
            #~ else:
                #~ raise osv.except_osv(_('Warning !'), _(
                    #~ 'Not found a sequence of configuration. %s !') % (msg2))
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
            #~ now = time.strftime('%Y-%m-%d %H:%M:%S')
            #~ htz = int(self._get_time_zone(cr, uid, ids, context=context))
            #~ date_today = now and datetime.strptime(payslip.payslip_datetime, '%Y-%m-%d %H:%M:%S') + timedelta(hours=htz) or False
            # certificate_id = payslip.company_id.certificate_id
            #~ context.update({'date_work': payslip.payslip_datetime })
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
                    'Check date of invoice and the validity of certificate, & that the register of the certificate is active.\n!') )
        
        #~ invoice_datetime = self.browse(cr, uid, ids)[0].invoice_datetime
        #~ ir_seq_app_obj = self.pool.get('ir.sequence.approval')
        #~ invoice = self.browse(cr, uid, ids[0], context=context)
        #~ sequence_app_id = ir_seq_app_obj.search(cr, uid, [(
            #~ 'sequence_id', '=', invoice.invoice_sequence_id.id)], context=context)
        #~ if sequence_app_id:
            #~ type_inv = ir_seq_app_obj.browse(
                #~ cr, uid, sequence_app_id[0], context=context).type
        #~ if invoice_datetime < '2012-07-01 00:00:00':
            #~ return file_globals
        #~ elif 'cfd' in type_inv and not 'cfdi' in type_inv:
            #~ # Search char "," for addons_path, now is multi-path
            #~ all_paths = tools.config["addons_path"].split(",")
            #~ for my_path in all_paths:
                #~ if os.path.isdir(os.path.join(my_path, 'l10n_mx_facturae_base', 'SAT')):
                    #~ # If dir is in path, save it on real_path
                    #~ file_globals['fname_xslt'] = my_path and os.path.join(
                        #~ my_path, 'l10n_mx_facturae_base', 'SAT',
                        #~ 'cadenaoriginal_2_2_l.xslt') or ''
                    #~ break
        #~ elif 'cfdi' in type_inv:
            #~ # Search char "," for addons_path, now is multi-path
            all_paths = tools.config["addons_path"].split(",")
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
        year = float(time.strftime('%Y', time.strptime(
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

    def _get_facturae_payroll_xml_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        payroll = self.browse(cr, uid, ids)[0]
        invoice_obj = self.pool.get('account.invoice')
        if payroll:
            facturae_version = '11'
            facturae_type='nomina'
            context.update(self._get_file_globals(cr, uid, ids, context=context))
            htz = int(self._get_time_zone(cr, uid, ids, context=context))
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            date_now = now and datetime.strptime(payroll.payslip_datetime, '%Y-%m-%d %H:%M:%S') + timedelta(hours=htz) or False
            date_now = time.strftime('%Y-%m-%dT%H:%M:%S', time.strptime(str(date_now), '%Y-%m-%d %H:%M:%S')) or False
            context.update({'fecha': date_now or ''})
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
                'time': time,
                'employee': payroll.employee_id,
                'noCertificado': noCertificado,
                'formaDePago': formaDePago,
                'certificado': cert_str,
                'fecha':  time.strftime('%Y-%m-%dT%H:%M:%S', time.strptime(str(payroll.date_payslip_tz), '%Y-%m-%d %H:%M:%S'))
                }
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
                invoice_obj.validate_scheme_facturae_xml(cr, uid, ids, [data_xml], 'v3.2', 'cfd')
            except Exception, e:
                raise orm.except_orm(_('Warning'), _('Parse Error XML: %s.') % (e))
            for my_path in all_paths:
                if os.path.isdir(os.path.join(my_path, 'l10n_mx_payroll_base', 'template')):
                    fname_jinja_tmpl = my_path and os.path.join(my_path, 'l10n_mx_payroll_base', 'template', 'nomina11' + '.xml') or ''
            dictargs = {
                'a': payroll,
                'employee': payroll.employee_id,
                'time': time,
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
                invoice_obj.validate_scheme_facturae_xml(cr, uid, ids, [data_xml_payroll], facturae_version, facturae_type)
            except Exception, e:
                raise orm.except_orm(_('Warning'), _('Parse Error XML: %s.') % (e))
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
            sign_str = invoice_obj._get_sello(cr=False, uid=False, ids=False, context=context)
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
            'cfdi_xml': False,
            'cfdi_folio_fiscal': False,
            'pac_id': False,
        })
        return super(hr_payslip, self).copy(cr, uid, id, default, context=context)
