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

class hr_payslip_product_line(osv.Model):
    
    _name = 'hr.payslip.product.line'

    _columns = {
        'payslip_id': fields.many2one('hr.payslip'),
        'product_id': fields.many2one('product.product', 'Product'),
        'amount': fields.float('Amount')
    }

class hr_payslip(osv.Model):

    _inherit = 'hr.payslip'

    _columns = {
        'journal_id': fields.many2one('account.journal','Journal'),
        'date_payslip': fields.date('Payslip Date'),
        'payslip_datetime': fields.datetime('Electronic Payslip Date'),
        'line_payslip_product_ids': fields.one2many('hr.payslip.product.line', 'payslip_id', 'Generic Product'),
        'pay_method_id': fields.many2one('pay.method', 'Payment Method',
            readonly=True, states={'draft': [('readonly', False)]}),
    }

    def hr_verify_sheet(self, cr, uid, ids, context=None):
        super(hr_payslip, self).hr_verify_sheet(cr, uid, ids)
        result = self.create_ir_attachment_payroll(cr, uid, ids, context)
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
            approval_id = payroll.journal_id and payroll.journal_id.sequence_id and \
                payroll.journal_id.sequence_id.approval_ids[0] and \
                        payroll.journal_id.sequence_id.approval_ids[0] or False
            if approval_id:
                if payroll.employee_id.address_home_id:
                    type = payroll.journal_id and payroll.journal_id.sequence_id and \
                            payroll.journal_id.sequence_id.approval_ids[0] and \
                                        payroll.journal_id.sequence_id.approval_ids[0].type
                    attach_ids.append( ir_attach_obj.create(cr, uid, {
                          'name': payroll.number or '/', 'type': type,
                          'journal_id': payroll.journal_id and payroll.journal_id.id or False,
                          'payroll_id': payroll and payroll.id or False},
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

    def conv_ascii(self, cr, uid, ids, text):
        """
        @param text : text that need convert vowels accented & characters to ASCII
        Converts accented vowels, ñ and ç to their ASCII equivalent characters
        """
        old_chars = [
            'á', 'é', 'í', 'ó', 'ú', 'à', 'è', 'ì', 'ò', 'ù', 'ä', 'ë', 'ï', 'ö',
            'ü', 'â', 'ê', 'î', 'ô', 'û', 'Á', 'É', 'Í', 'Ó', 'Ú', 'À', 'È', 'Ì',
            'Ò', 'Ù', 'Ä', 'Ë', 'Ï', 'Ö', 'Ü', 'Â', 'Ê', 'Î', 'Ô', 'Û', 'ñ', 'Ñ',
            'ç', 'Ç', 'ª', 'º', '°', ' ', 'Ã', 'Ø', '&'
        ]
        new_chars = [
            'a', 'e', 'i', 'o', 'u', 'a', 'e', 'i', 'o', 'u', 'a', 'e', 'i', 'o',
            'u', 'a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U', 'A', 'E', 'I',
            'O', 'U', 'A', 'E', 'I', 'O', 'U', 'A', 'E', 'I', 'O', 'U', 'n', 'N',
            'c', 'C', 'a', 'o', 'o', ' ', 'A', '0' ,'y'
        ]
        for old, new in zip(old_chars, new_chars):
            try:
                text = text.replace(unicode(old, 'UTF-8'), new)
            except:
                try:
                    text = text.replace(old, new)
                except:
                    raise osv.except_osv(_('Warning !'), _(
                        "Can't recode the string [%s] in the letter [%s]") % (text, old))
        return text

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

    def _get_dict_payroll(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        payrolls = self.browse(cr, uid, ids, context=context)
        list_data = []
        department = ''
        for p in self.browse(cr, uid, ids, context=context):
            dict_data = {}
            tipoComprobante = 'egreso'
            # Inicia seccion: Nomina
            htz = int(self._get_time_zone(cr, uid, [p.id], context=context))
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            date_now = now and datetime.strptime(p.payslip_datetime, '%Y-%m-%d %H:%M:%S') + timedelta(hours=htz) or False
            date_now = time.strftime('%Y-%m-%d', time.strptime(str(date_now), '%Y-%m-%d %H:%M:%S')) or False
            number_of_days=0
            worked_days_line_ids = p.worked_days_line_ids
            if worked_days_line_ids:
                for n in worked_days_line_ids:
                    number_of_days += n['number_of_days']
            if p.employee_id.department_id:
                department = p.employee_id.department_id.name
                department = self.conv_ascii(cr, uid, ids, department)
            dict_data['nomina:Nomina'] = {}
            dict_data['nomina:Nomina'].update({
                'RegistroPatronal': p.employee_id.employer_registration and \
                p.employee_id.employer_registration.replace('\n\r', ' ').replace(
                    '\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A',
                'NumEmpleado': p.employee_id.identification_id or 'S/N',
                'CURP': p.employee_id.curp and \
                            p.employee_id.curp.replace('\n\r', ' ').replace(
                                '\r\n', ' ').replace('\n', ' ').replace('\r', ' ').upper() or 'S/N',
                'TipoRegimen': p.employee_id.regime_id.code and\
                                   p.employee_id.regime_id.code or '2',
                'NumSeguridadSocial':p.employee_id.nss and \
                            p.employee_id.nss.replace('\n\r', ' ').replace(
                                '\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'S/N',
                'FechaPago': date_now or False,
                'FechaInicialPago': p.date_from or False,
                'FechaFinalPago': p.date_to or False,
                'FechaInicioRelLaboral': p.contract_id.date_start and \
                                            p.contract_id.date_start or False,
                'NumDiasPagados': number_of_days or 0.0,
                'Departamento': department or 'N/A',
                'CLABE': p.employee_id.bank_account_id.clabe and \
                        p.employee_id.bank_account_id.clabe.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '000000000000000000',
                'Banco': p.employee_id.bank_account_id.bank and \
                            p.employee_id.bank_account_id.bank.code.replace(
                                '\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace(
                                        '\r', ' ') or '001',
                'Antiguedad':p.employee_id.seniority or 0,
                'Puesto': p.employee_id.job_id.name and \
                                p.contract_id.job_id.name or 'N/A',
                'TipoContrato': p.contract_id.type_id.name or '',
                'TipoJornada': p.contract_id.working_day_id.name or '',
                'PeriodicidadPago': p.contract_id.schedule_pay or '',
                'RiesgoPuesto': p.contract_id.risk_rank_id.code or '1',
                'SalarioBaseCotApor': p.contract_id.wage or 0,
                'SalarioDiarioIntegrado': p.contract_id.integrated_salary or 0,
                'xmlns:nomina':'http://www.sat.gob.mx/nomina',
                'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                'Version': '1.1'
            })
            input_line_ids = p.input_line_ids
            if input_line_ids:
                TotalGravado_percepcion = 0
                TotalExento_percepcion = 0
                TotalExento_deduccion = 0
                TotalGravado_deduccion = 0
                lista_percepciones = []
                lista_deducciones = []
                var = 0
                percepciones_data = dict_data['nomina:Nomina']
                percepciones_data['nomina:Percepciones'] = {}
                deducciones_data = dict_data['nomina:Nomina']
                deducciones_data['nomina:Deducciones'] = {}
                for n in input_line_ids:
                    if n['salary_rule_id']['type_concept']=='perception':
                        concepto = self.conv_ascii(cr, uid, ids, n['salary_rule_id']['name'])
                        data_percepciones = {
                                        'TipoPercepcion': n['salary_rule_id']['code'],
                                        'Clave': n['salary_rule_id']['code']+'clave',
                                        'Concepto': concepto or '',
                                        'ImporteGravado': n['amount'],
                                        'ImporteExento': n['exempt_amount']
                                        }
                        TotalGravado_percepcion +=  n['amount']
                        TotalExento_percepcion +=  n['exempt_amount']
                        lista_percepciones.append(data_percepciones)
                    if n['salary_rule_id']['type_concept']=='deduction':
                        concepto = self.conv_ascii(cr, uid, ids, n['salary_rule_id']['name'])
                        data_deducciones = {
                                        'TipoDeduccion': n['salary_rule_id']['code'],
                                        'Clave': n['salary_rule_id']['clave'] or '',
                                        'Concepto': concepto or '',
                                        'ImporteGravado': n['amount'],
                                        'ImporteExento': n['exempt_amount'],
                                        }
                        TotalGravado_deduccion +=  n['amount']
                        TotalExento_deduccion += n['exempt_amount']
                        lista_deducciones.append(data_deducciones)
                percepciones_data['nomina:Percepciones'].update({
                                            'TotalGravado': TotalGravado_percepcion,
                                            'TotalExento': TotalExento_percepcion,
                                            'nomina:Percepcion' : lista_percepciones,
                                                        })

                deducciones_data['nomina:Deducciones'].update({
                                            'TotalGravado': TotalGravado_deduccion,
                                            'TotalExento': TotalExento_deduccion,
                                            'nomina:Deduccion' : lista_deducciones,
                                                        })
            else:
                raise orm.except_orm(_('Warning'), _('The payroll not have deductions or perceptions'))
            inability_line_ids = p.inability_line_ids
            if inability_line_ids:
                lista_incapacidades = []
                descuento = 0
                number_of_days = 0
                incapacidades_data = dict_data['nomina:Nomina']
                incapacidades_data['nomina:Incapacidades'] = {}
                for n in inability_line_ids:
                    descuento += n['amount']
                    number_of_days += n['number_of_days']
                    data_incapacidades = {
                                        'DiasIncapacidad': n['number_of_days'] or 0,
                                        'TipoIncapacidad': n['inability_id']['code'] or 1,
                                        'Descuento': n['amount'] or 0,
                                        }
                    lista_incapacidades.append(data_incapacidades)
                incapacidades_data['nomina:Incapacidades'].update({
                                                    'nomina:Incapacidad' : lista_incapacidades
                                                            })
            overtime_line_ids = p.overtime_line_ids
            if overtime_line_ids:
                lista_horasextras = []
                ImportePagado = 0
                number_of_days = 0
                number_of_hours = 0
                horasextras_data = dict_data['nomina:Nomina']
                horasextras_data['nomina:HorasExtras'] = {}
                for n in overtime_line_ids:
                    ImportePagado += n['amount']
                    number_of_days += n['number_of_days']
                    number_of_hours += n['number_of_hours']
                    if n['type_hours'] == 'double':
                        TipoHoras = 'Dobles'
                    if n['type_hours'] == 'triples':
                        TipoHoras = 'Triples'
                    data_horasextras = {'Dias': n['number_of_days'] or 0,
                                        'TipoHoras': TipoHoras,
                                        'HorasExtra': n['number_of_hours'] or 0,
                                        'ImportePagado': n['amount'] or 0,
                                        }
                    lista_horasextras.append(data_horasextras)
                horasextras_data['nomina:HorasExtras'].update({
                                            'nomina:HorasExtra' : lista_horasextras
                                                            })
        list_data.append(dict_data)
        return list_data


    def _get_facturae_payroll_xml_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        payroll = self.browse(cr, uid, ids)[0]
        invoice_obj = self.pool.get('account.invoice')
        if payroll:
            facturae_version = '11'
            facturae_type='nomina'
            data_dict_payroll = self._get_dict_payroll(cr, uid, ids, context=context)[0]
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(os.path.join(my_path, 'l10n_mx_payroll_base', 'template')):
                    fname_jinja_tmpl = my_path and os.path.join(my_path, 'l10n_mx_payroll_base', 'template', 'nomina11' + '.xml') or ''
            dictargs = {
                'o': data_dict_payroll,
                'time': time,
                }
            payroll = "payroll"
            (fileno_xml, fname_xml) = tempfile.mkstemp('.xml', 'openerp_' + (payroll or '') + '__facturae__')
            if fname_jinja_tmpl:
                with open(fname_jinja_tmpl, 'r') as f_jinja_tmpl:
                    jinja_tmpl_str = f_jinja_tmpl.read().encode('utf-8')
                    tmpl = jinja2.Template( jinja_tmpl_str )
                    with open(fname_xml, 'w') as new_xml:
                        new_xml.write( tmpl.render(**dictargs) )
            with open(fname_xml,'rb') as b:
                data_xml_payroll = b.read().encode('utf-8')
            try:
                invoice_obj.validate_scheme_facturae_xml(cr, uid, ids, [data_xml_payroll], facturae_version, facturae_type)
            except Exception, e:
                raise orm.except_orm(_('Warning'), _('Parse Error XML: %s.') % (e))
            #Agregar nodo Nomina en nodo Complemento
            doc_xml_payroll = xml.dom.minidom.parseString(data_xml_payroll)
            complemento = """<cfdi:Complemento xmlns:cfdi="http://www.sat.gob.mx/cfd/3"></cfdi:Complemento>"""
            cfdi_complemento = xml.dom.minidom.parseString(complemento)
            complemento = cfdi_complemento.documentElement
            nomina = doc_xml_payroll.getElementsByTagName('nomina:Nomina')[0]
            complemento.appendChild(nomina)
            data_xml = complemento.toxml('UTF-8')
            doc_xml = xml.dom.minidom.parseString(data_xml)
            #Falta Agregar Nodo Complemento en Nodo Comprobante
            #doc_xml = xml.dom.minidom.parseString(data_xml)
            #doc_xml_comprobante = doc_xml.documentElement
            #doc_xml_comprobante.appendChild(complemento)
            #data_xml = doc_xml_comprobante.toxml('UTF-8')
            #doc_xml_full = xml.dom.minidom.parseString(data_xml)
            payroll = "payroll"
            (fileno_xml, fname_xml) = tempfile.mkstemp('.xml', 'openerp_' + (payroll or '') + '__facturae__')
            fname_txt = fname_xml + '.txt'
            f = open(fname_xml, 'w')
            doc_xml.writexml(f, indent='    ', addindent='    ', newl='\r\n', encoding='UTF-8')
            f.close()
            os.close(fileno_xml)
            (fileno_sign, fname_sign) = tempfile.mkstemp('.txt', 'openerp_' + (
                payroll or '') + '__facturae_txt_md5__')
            os.close(fileno_sign)
            context.update({
                'fname_xml': fname_xml,
                'fname_txt': fname_txt,
                'fname_sign': fname_sign,
            })
            #context.update({'fecha': data_dict_payroll['cfdi:Comprobante']['fecha']}) #No borrar se va a ocupar
            context.update({'fecha': '2014-01-27T20:20:20'})
            #~sign_str = invoice_obj._get_sello(cr=False, uid=False, ids=False, context=context)
            #~nodeComprobante = doc_xml_full.getElementsByTagName("cfdi:Comprobante")[0]
            #~nodeComprobante.setAttribute("sello", sign_str)
            #~data_xml_with_payroll = doc_xml_full.documentElement
            data_xml = doc_xml.toxml('UTF-8')
            data_xml = codecs.BOM_UTF8 + data_xml
            print data_xml
        return fname_xml, data_xml
