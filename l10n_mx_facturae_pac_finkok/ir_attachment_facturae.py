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
    
    def _finkok_cancel(self, cr, uid, ids, context=None):
        msg = ''
        folio_cancel = ''
        UUIDS = []
        status = False
        pac_params_obj = self.pool.get('params.pac')
        dict_error = {'202' : _('UUID previously canceled'), '203' : _('UUID does not match the RFC\
            sender neither of the applicant'), '205' : _('Not exist UUID'),
            '708' : _('Could not connect to the SAT')}
        for ir_attachment_facturae_mx_id in self.browse(cr, uid, ids, context=context):
            status = False
            pac_params_ids = pac_params_obj.search(cr, uid, [
                ('method_type', '=', 'cancelar'),
                ('res_pac', '=', ir_attachment_facturae_mx_id.res_pac.id),
                #~ ('company_id', '=', invoice.company_emitter_id.id),
                ('company_id', '=', ir_attachment_facturae_mx_id.company_id.id),
                ('active', '=', True),
            ], limit=1, context=context)
            pac_params_id = pac_params_ids and pac_params_ids[0] or False
            taxpayer_id = ir_attachment_facturae_mx_id.company_id.vat[2::] or ir_attachment_facturae_mx_id.company_id.partner_id.vat[2::] or False
            if pac_params_id:
                pac_params_brw = pac_params_obj.browse(cr, uid, [pac_params_id], context=context)[0]
                username = pac_params_brw.user or ir_attachment_facturae_mx_id.res_pac.user
                password = pac_params_brw.password or ir_attachment_facturae_mx_id.res_pac.password
                wsdl_url = pac_params_brw.url_webservice or ir_attachment_facturae_mx_id.res_pac.url_webservice
                namespace = pac_params_brw.namespace or ir_attachment_facturae_mx_id.res_pac.namespace
                if 'demo' in wsdl_url or 'testing' in wsdl_url:
                    msg += _(u'WARNING, CANCEL IN TEST!!!!')
                cerCSD_file = self.binary2file(cr, uid, ids,
                        ir_attachment_facturae_mx_id.certificate_file, 'openerp_' + '' + '__certificate__',
                        '.cer')
                keyCSD_file = self.binary2file(cr, uid, ids,
                        ir_attachment_facturae_mx_id.certificate_key_file, 'openerp_' +'' + '__key__',
                        '.key')
                (fileno_xml, fname_key_encry_pem) = tempfile.mkstemp('.key.encryp', 'openerp_' + '__key_encryp__')
                with open(cerCSD_file, 'r') as cer_file:
                    cerCSD = cer_file.read()
                cmd = 'openssl rsa -in %s -des3 -out %s -passout pass:%s' %(keyCSD_file, fname_key_encry_pem, password)
                args = tuple(cmd.split(' '))
                input, output = exec_command_pipe(*args)
                time.sleep(2)
                f = open(fname_key_encry_pem)
                data = f.read()
                f.close()
                keyCSD = base64.encodestring(data)
                try:            
                    client = Client(wsdl_url, cache=None)
                except:
                    raise orm.except_orm(_('Warning'), _('Connection lost, verify your internet conection or verify your PAC'))
                folio_cancel = ir_attachment_facturae_mx_id.cfdi_folio_fiscal
                UUIDS.append(folio_cancel)
                UUIDS_list = client.factory.create("UUIDS")
                UUIDS_list.uuids.string = UUIDS
                params = [UUIDS_list, username, password, taxpayer_id, cerCSD.encode('base64'), keyCSD]
                result = client.service.cancel(*params)
                get_receipt = [username, password, taxpayer_id, folio_cancel]
                query_pending_cancellation = [username, password, folio_cancel]
                get_receipt = client.service.get_receipt(*get_receipt)
                query_pending_cancellation = client.service.query_pending_cancellation(*query_pending_cancellation)
                time.sleep(1)
                if not 'Folios' in result:
                    msg += _('%s' %result)
                    raise orm.except_orm(_('Warning'), _('Mensaje %s') % (msg))
                else:
                    EstatusUUID = result.Folios[0][0].EstatusUUID
                    if EstatusUUID == '201':
                        msg += _('\n- The process of cancellation has completed correctly.\n\
                                    The uuid cancelled is: ') + folio_cancel
                        self.write(cr, uid, [ir_attachment_facturae_mx_id.id], {
                                        'cfdi_fecha_cancelacion': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
                        status = True
                    else:
                        if EstatusUUID in dict_error:
                            if not ('demo' in wsdl_url or 'testing' in wsdl_url):
                                raise orm.except_orm(_('Warning'), _('Mensaje %s %s Code: %s') % (msg, dict_error[EstatusUUID], EstatusUUID))
                            else:
                                 msg += _('Mensaje %s %s Code: %s') % (msg, dict_error[EstatusUUID], EstatusUUID)
            else:
                msg = _('Not found information of webservices of PAC, verify that the configuration of PAC is correct')
        return {'message': msg, 'status': status}
    
    def _finkok_stamp(self, cr, uid, ids, fdata=None, context=None):
        """
        @params fdata : File.xml codification in base64
        """
        if context is None:
            context = {}
        pac_params_obj = self.pool.get('params.pac')
        for ir_attachment_facturae_mx_id in self.browse(cr, uid, ids, context=context):
            comprobante = 'cfdi:Comprobante'
            cfd_data = base64.decodestring(fdata or ir_attachment_facturae_mx_id.file_input.index_content)
            if tools.config['test_report_directory']:#TODO: Add if test-enabled:
                ir_attach_facturae_mx_file_input = ir_attachment_facturae_mx_id.file_input and ir_attachment_facturae_mx_id.file_input or False
                fname_suffix = ir_attach_facturae_mx_file_input and ir_attach_facturae_mx_file_input.datas_fname or ''
                open( os.path.join(tools.config['test_report_directory'], 'l10n_mx_facturae_pac_finkok' + '_' + \
                  'before_upload' + '-' + fname_suffix), 'wb+').write( cfd_data )
            file = False
            msg = ''
            folio_fiscal = ''
            cfdi_xml = False
            status = False
            pac_params_ids = pac_params_obj.search(cr, uid, [
                ('method_type', '=', 'firmar'), 
                ('company_id', '=', ir_attachment_facturae_mx_id.company_id.id),
                ('res_pac', '=', ir_attachment_facturae_mx_id.res_pac.id),
                ('active', '=', True)], limit=1, context=context)
            if pac_params_ids:
                pac_params = pac_params_obj.browse(
                    cr, uid, pac_params_ids, context)[0]
                user = pac_params.user or ir_attachment_facturae_mx_id.res_pac.user
                password = pac_params.password or ir_attachment_facturae_mx_id.res_pac.password
                wsdl_url = pac_params.url_webservice or ir_attachment_facturae_mx_id.res_pac.url_webservice
                namespace = pac_params.namespace or ir_attachment_facturae_mx_id.res_pac.namespace
                certificate_link = pac_params.certificate_link
                #agregar otro campo para la URL de testing y poder validar sin cablear
                url_finkok = 'http://facturacion.finkok.com/servicios/soap/stamp.wsdl'
                testing_url_finkok = 'http://demo-facturacion.finkok.com/servicios/soap/stamp.wsdl'
                #~ Dir_pac=http://demo-facturacion.finkok.com/servicios/soap/stamp.wsdl
                #~ usuario=isaac@vauxoo.com
                #Contraseña=1Q2W3E4R5t_
                if (wsdl_url == url_finkok) or (wsdl_url == testing_url_finkok):
                    pass
                else:
                    raise osv.except_osv(_('Warning'), _('Web Service URL o PAC incorrect'))
                #~ if namespace == 'http://facturacion.finkok.com/stamp':
                    #~ pass
                #~ else:
                    #~ raise osv.except_osv(_('Warning'), _('Namespace of PAC incorrect'))
                if 'demo' in wsdl_url or 'testing' in wsdl_url:
                    msg += _(u'WARNING, SIGNED IN TEST!!!!\n\n' + wsdl_url)
                incidencias = False
                try:            
                    client = Client(wsdl_url, cache=None)
                except:
                    raise orm.except_orm(_('Warning'), _('Connection lost, verify your internet conection or verify your PAC'))
                try:
                    cfdi = base64.encodestring(cfd_data)
                    zip = False
                    params = [cfdi, user, password]
                    resultado = client.service.stamp(*params)
                    if not resultado.Incidencias or None:
                        msg += _(tools.ustr(resultado.CodEstatus))
                        folio_fiscal = resultado.UUID or False
                        msg +=".Folio Fiscal: " + resultado.UUID + "."
                        fecha_timbrado = resultado.Fecha or False
                        rfc_emitter = ir_attachment_facturae_mx_id.company_id and ir_attachment_facturae_mx_id.company_id.partner_id and ir_attachment_facturae_mx_id.company_id.partner_id.vat_split or ""
                        rfc_receiver =  ir_attachment_facturae_mx_id.partner_id and ir_attachment_facturae_mx_id.partner_id.vat_split or ""
                        cbb = self.pool.get('ir.attachment.facturae.mx')._create_qrcode(cr, uid, ids, rfc_emitter, rfc_receiver, folio_fiscal, context=context)
                        original_string = self.pool.get('ir.attachment.facturae.mx')._create_original_str(cr, uid, ids, resultado, context=context)
                        cfdi_data = {
                            'cfdi_sello': resultado.SatSeal or False,
                            'cfdi_no_certificado': resultado.NoCertificadoSAT or False,
                            'cfdi_fecha_timbrado': resultado.Fecha or False,
                            #'cfdi_xml': resultado.xml.encode('ascii', 'xmlcharrefreplace') or '',  # este se necesita en uno que no es base64, ademas no se ve funcionalidad de este campo
                            'cfdi_folio_fiscal': folio_fiscal,
                            'pac_id': pac_params.id,
                            #~'cfdi_cbb': open(cbb).read().encode('base64'),# ya lo regresa en base64, ya se crea qr desde funcion
                            'cfdi_cadena_original': original_string or False,
                            'certificate_link': certificate_link or False,
                        }
                        cfdi_xml = resultado.xml.encode('ascii', 'xmlcharrefreplace') or ''
                        comprobante_new = '</'+comprobante+'>'
                        msg += _(
                                u"\nMake Sure to the file really has generated correctly to the SAT\nhttps://www.consulta.sat.gob.mx/sicofi_web/moduloECFD_plus/ValidadorCFDI/Validador%20cfdi.html")
                        if cfdi_xml:
                            url_pac = '%s<!--Para validar el XML CFDI puede descargar el certificado del PAC desde la siguiente liga: https://liga que proporcione finkok-->' % (
                                comprobante_new)
                            cfdi_xml = cfdi_xml.replace(comprobante_new, url_pac)
                            file = base64.encodestring(cfdi_xml or '')
                            self.write(cr, uid, ids, cfdi_data)
                            status = True
                        else:
                            msg += _(u"Can't extract the file XML of PAC")
                    else:
                        incidencias = resultado.Incidencias.Incidencia[0]
                        raise orm.except_orm(_('Warning'), _('Incidencias: %s.') % (incidencias))
                except Exception, e:
                    if incidencias:
                        raise orm.except_orm(_('Warning'), _('Error al timbrar XML, Incidencias: %s.') % (incidencias))
                    else:
                        raise orm.except_orm(_('Warning'), _('Error al timbrar XML: %s.') % (e))
            else:
                msg += 'Not found information from web services of PAC, verify that the configuration of PAC is correct'
                raise osv.except_osv(_('Warning'), _(
                    'Not found information from web services of PAC, verify that the configuration of PAC is correct'))
            return {'file': file, 'msg': msg, 'cfdi_xml': cfdi_xml, 'status': status, 'cfdi_data': cfdi_data}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
