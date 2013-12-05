# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@vauxoo.com
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tools.translate import _
from openerp.osv import fields, osv, orm
from openerp import tools
from openerp import netsvc
from openerp.tools.misc import ustr
import base64
import xml.dom.minidom
import time
import StringIO
import csv
import tempfile
import os
import sys
import codecs
from xml.dom import minidom
import urllib
import pooler
from openerp.tools.translate import _
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import time
from openerp import tools
import logging
_logger = logging.getLogger(__name__)
try:
    from SOAPpy import WSDL
except:
    _logger.error('Install SOAPpy "sudo apt-get install python-soappy" to use l10n_mx_facturae_pac_finkok module.')
try:
    from suds.client import Client
except:
    _logger.error('Install suds to use l10n_mx_facturae_pac_finkok module.')

def exec_command_pipe(*args):
        # Agregue esta funcion, ya que con la nueva funcion original, de tools no funciona
        # TODO: Hacer separacion de argumentos, no por espacio, sino tambien por "
        # ", como tipo csv, pero separator espace & delimiter "
        cmd = ' '.join(args)
        if os.name == "nt":
            cmd = cmd.replace(
                '"', '')  # provisionalmente, porque no funcionaba en win32
        return os.popen2(cmd, 'b')
        
class ir_attachment_facturae_mx(osv.Model):
    _inherit = 'ir.attachment.facturae.mx'

    

    def _get_type(self, cr, uid, ids=None, context=None):
        types = super(ir_attachment_facturae_mx, self)._get_type(
            cr, uid, ids, context=context)
        types.extend([
            ('cfdi32_pac_finkok', 'CFDI 3.2 Finkok'),
        ])
        return types
    
    def get_driver_fc_sign(self):
        factura_mx_type__fc = super(ir_attachment_facturae_mx, self).get_driver_fc_sign()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi32_pac_finkok': self._finkok_stamp})
        return factura_mx_type__fc
    
    def get_driver_fc_cancel(self):
        factura_mx_type__fc = super(ir_attachment_facturae_mx, self).get_driver_fc_cancel()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi32_pac_finkok': self._finkok_cancel})
        return factura_mx_type__fc
        
    _columns = {
        'type': fields.selection(_get_type, 'Type', type='char', size=64,
                                 required=True, readonly=True, help="Type of Electronic Invoice"),
    }
    
    def _finkok_cancel(self, cr, uid, ids, context=None):
        msg = ''
        folio_cancel = ''
        invoices = []
        certificate_obj = self.pool.get('res.company.facturae.certificate')
        pac_params_obj = self.pool.get('params.pac')
        invoice_obj = self.pool.get('account.invoice')
        dict_error = {'202' : _('UUID previously canceled'), '203' : _('UUID does not match the RFC\
            sender neither of the applicant'), '205' : _('Not exist UUID'),
            '708' : _('Could not connect to the SAT')}
        for ir_attachment_facturae_mx_id in self.browse(cr, uid, ids, context=context):
            status = False
            invoice = ir_attachment_facturae_mx_id.invoice_id
            pac_params_ids = pac_params_obj.search(cr, uid, [
                ('method_type', '=', 'pac_finkok_cancelar'),
                ('company_id', '=', invoice.company_emitter_id.id),
                ('active', '=', True),
            ], limit=1, context=context)
            pac_params_id = pac_params_ids and pac_params_ids[0] or False
            taxpayer_id = invoice.company_id.vat[2::] or invoice.company_id.partner_id.vat[2::] or False
            if pac_params_id:
                file_globals = invoice_obj._get_file_globals(cr, uid, [invoice.id], context=context)
                pac_params_brw = pac_params_obj.browse(cr, uid, [pac_params_id], context=context)[0]
                username = pac_params_brw.user
                password = pac_params_brw.password
                wsdl_url = pac_params_brw.url_webservice
                namespace = pac_params_brw.namespace
                if 'demo' in wsdl_url or 'testing' in wsdl_url:
                    msg += _(u'WARNING, CANCEL IN TEST!!!!')
                fname_cer_no_pem = file_globals['fname_cer']
                cerCSD = open(fname_cer_no_pem).read().encode('base64')
                fname_key_no_pem = file_globals['fname_key']
                fname_key_encry_pem = fname_key_no_pem.replace('.key', '.key.encryp')
                cmd = 'openssl rsa -in %s -des3 -out %s -passout pass:%s' %(fname_key_no_pem, fname_key_encry_pem, password)
                args = tuple(cmd.split(' '))
                input, output = exec_command_pipe(*args)
                time.sleep(2)
                f = open(fname_key_encry_pem)
                data = f.read()
                f.close()
                keyCSD = base64.encodestring(data)
                client = Client(wsdl_url, cache=None)
                folio_cancel = invoice.cfdi_folio_fiscal
                invoices.append(folio_cancel)
                invoices_list = client.factory.create("UUIDS")
                invoices_list.uuids.string = invoices
                params = [invoices_list, username, password, taxpayer_id, cerCSD, keyCSD]
                result = client.service.cancel(*params)
                if not 'Folios' in result:
                    msg += _('%s' %result.CodEstatus)
                    if not ('demo' in wsdl_url or 'testing' in wsdl_url):
                        raise orm.except_orm(_('Warning'), _('Mensaje %s') % (msg))
                else:
                    EstatusUUID = result.Folios[0][0].EstatusUUID
                    if EstatusUUID == '201':
                        msg += _('\n- The process of cancellation has completed correctly.\n\
                                    The uuid cancelled is: ') + folio_cancel
                        invoice_obj.write(cr, uid, [invoice.id], {
                                        'cfdi_fecha_cancelacion': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
                    else:
                        if EstatusUUID in dict_error:
                            raise orm.except_orm(_('Warning'), _('Mensaje %s %s Code: %s') % (msg, dict_error[EstatusUUID], EstatusUUID))
            else:
                msg = _('Not found information of webservices of PAC, verify that the configuration of PAC is correct')
        return {'message': msg}
    
    def _finkok_stamp(self, cr, uid, ids, fdata=None, context={}):
        """
        @params fdata : File.xml codification in base64
        """
        invoice_obj = self.pool.get('account.invoice')
        pac_params_obj = self.pool.get('params.pac')
        for ir_attachment_facturae_mx_id in self.browse(cr, uid, ids, context=context):
            invoice = ir_attachment_facturae_mx_id.invoice_id
            comprobante = invoice_obj._get_type_sequence(
                cr, uid, [invoice.id], context=context)
            cfd_data = base64.decodestring(fdata or invoice_obj.fdata)
            if tools.config['test_report_directory']:#TODO: Add if test-enabled:
                ir_attach_facturae_mx_file_input = ir_attachment_facturae_mx_id.file_input and ir_attachment_facturae_mx_id.file_input or False
                fname_suffix = ir_attach_facturae_mx_file_input and ir_attach_facturae_mx_file_input.datas_fname or ''
                open( os.path.join(tools.config['test_report_directory'], 'l10n_mx_facturae_pac_finkok' + '_' + \
                  'before_upload' + '-' + fname_suffix), 'wb+').write( cfd_data )
            date = invoice.date_invoice
            date_format = datetime.strptime(
                date, '%Y-%m-%d').strftime('%Y-%m-%d')
            context['date'] = date_format
            invoice_ids = [invoice.id]
            file = False
            msg = ''
            folio_fiscal = ''
            cfdi_xml = False
            pac_params_ids = pac_params_obj.search(cr, uid, [
                ('method_type', '=', 'pac_finkok_firmar'), (
                    'company_id', '=', invoice.company_emitter_id.id), (
                        'active', '=', True)], limit=1, context=context)
            if pac_params_ids:
                pac_params = pac_params_obj.browse(
                    cr, uid, pac_params_ids, context)[0]
                user = pac_params.user
                password = pac_params.password
                wsdl_url = pac_params.url_webservice
                namespace = pac_params.namespace
                #agregar otro campo para la URL de testing y poder validar sin cablear
                url_finkok = 'http://facturacion.finkok.com/servicios/soap/stamp.wsdl'
                testing_url_finkok = 'http://demo-facturacion.finkok.com/servicios/soap/stamp.wsdl'
                #~ Dir_pac=http://demo-facturacion.finkok.com/servicios/soap/stamp.wsdl
                #~ usuario=isaac@vauxoo.com
                #Contraseña=1Q2W3E4R5t_
                if (wsdl_url == url_finkok) or (wsdl_url == testing_url_finkok):
                    pass
                else:
                    raise osv.except_osv(_('Warning'), _('Web Service URL \
                        o PAC incorrect'))
                #~ if namespace == 'http://facturacion.finkok.com/stamp':
                    #~ pass
                #~ else:
                    #~ raise osv.except_osv(_('Warning'), _('Namespace of PAC incorrect'))
                if 'demo' in wsdl_url or 'testing' in wsdl_url:
                    msg += _(u'WARNING, SIGNED IN TEST!!!!\n\n' + wsdl_url)
                client = Client(wsdl_url, cache=None)
                if True: # if wsdl_client:
                    file_globals = invoice_obj._get_file_globals(
                        cr, uid, invoice_ids, context=context)
                    fname_cer_no_pem = file_globals['fname_cer']
                    #cerCSD = open(fname_cer_no_pem).read().encode('base64') #Mejor forma de hacerlo
                    cerCSD = fname_cer_no_pem and base64.encodestring(
                        open(fname_cer_no_pem, "r").read()) or ''
                    fname_key_no_pem = file_globals['fname_key']
                    keyCSD = fname_key_no_pem and base64.encodestring(
                        open(fname_key_no_pem, "r").read()) or ''
                    #keyCSD = open(fname_key_no_pem).read().encode('base64') #Mejor forma de hacerlo
                    cfdi = base64.encodestring(cfd_data)
                    zip = False  # Validar si es un comprimido zip, con la extension del archivo
                    contrasenaCSD = file_globals.get('password', '')
                    params = [cfdi, user, password]
                    resultado = client.service.stamp(*params)
                    if not resultado.Incidencias or None:
                        msg += _(tools.ustr(resultado.CodEstatus))
                        folio_fiscal = resultado.UUID or False
                        msg +=".Folio Fiscal: " + resultado.UUID + "."
                        htz = int(invoice_obj._get_time_zone(
                        cr, uid, [ir_attachment_facturae_mx_id.invoice_id.id], context=context))
                        fecha_timbrado = resultado.Fecha or False
                        fecha_timbrado = fecha_timbrado and time.strftime(
                                '%Y-%m-%d %H:%M:%S', time.strptime(
                                    fecha_timbrado[:19], '%Y-%m-%dT%H:%M:%S')) or False
                        fecha_timbrado = fecha_timbrado and datetime.strptime(
                            fecha_timbrado, '%Y-%m-%d %H:%M:%S') + timedelta(hours=htz) or False                        
                        cfdi_data = {
                            'cfdi_sello': resultado.SatSeal or False,
                            'cfdi_no_certificado': resultado.NoCertificadoSAT or False,
                            'cfdi_fecha_timbrado': resultado.Fecha or False,
                            'cfdi_xml': resultado.xml or '',  # este se necesita en uno que no es base64
                            'cfdi_folio_fiscal': folio_fiscal,
                        }
                        if cfdi_data.get('cfdi_xml', False):
                            invoice_obj.write(cr, uid, [invoice.id], cfdi_data)
                        else:
                            msg += _(u"Can't extract the file XML of PAC")
                        cbb = invoice_obj._create_qrcode(cr, uid, ids,invoice.id, context=context)
                        original_string = invoice_obj._create_original_str(cr, uid, ids,invoice.id, context=context)
                        cfdi_data_cbb_os = {
                            'cfdi_cbb': open(cbb).read().encode('base64'),# ya lo regresa en base64
                            'cfdi_cadena_original': original_string or False,
                        }
                        invoice_obj.write(cr, uid, [invoice.id], cfdi_data_cbb_os)
                        comprobante_new = '</'+comprobante+'>'
                        msg += _(
                                u"\nMake Sure to the file really has generated correctly to the SAT\nhttps://www.consulta.sat.gob.mx/sicofi_web/moduloECFD_plus/ValidadorCFDI/Validador%20cfdi.html")
                        if cfdi_data.get('cfdi_xml', False):
                            #cambiar el link
                            url_pac = '%s<!--Para validar el XML CFDI puede descargar el certificado del PAC desde la siguiente liga: https://liga que proporcione finkok-->' % (
                                comprobante_new)
                            cfdi_data['cfdi_xml'] = cfdi_data[
                                'cfdi_xml'].replace(comprobante_new, url_pac)
                            file = base64.encodestring(cfdi_data['cfdi_xml'] or '')
                            cfdi_xml = cfdi_data.pop('cfdi_xml')

                    else:
                        inicidencias = resultado.Incidencias.Incidencia[0]
                        IdIncidencia = resultado.Incidencias.Incidencia[0]['IdIncidencia']
                        CodigoError = resultado.Incidencias.Incidencia[0]['CodigoError']
                        MensajeIncidencia = resultado.Incidencias.Incidencia[0]['MensajeIncidencia']
                        NoCertificadoPac = resultado.Incidencias.Incidencia[0]['NoCertificadoPac']
                        RfcEmisor = resultado.Incidencias.Incidencia[0]['RfcEmisor']
                        WorkProcessId = resultado.Incidencias.Incidencia[0]['WorkProcessId']
                        FechaRegistro = resultado.Incidencias.Incidencia[0]['FechaRegistro']
                        raise orm.except_orm(_('Warning'), _('Inicidencias: %s.') % (inicidencias))
                else:
                    raise orm.except_orm(_('Warning'), _('Not conexión'))
            else:
                msg += 'Not found information from web services of PAC, verify that the configuration of PAC is correct'
                raise osv.except_osv(_('Warning'), _(
                    'Not found information from web services of PAC, verify that the configuration of PAC is correct'))
            return {'file': file, 'msg': msg, 'cfdi_xml': cfdi_xml}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
