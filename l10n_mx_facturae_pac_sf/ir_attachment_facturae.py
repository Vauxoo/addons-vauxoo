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
import wizard
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
try:
    from SOAPpy import WSDL
except:
    print "Package SOAPpy missed"#TODO: Warning message
    pass

class ir_attachment_facturae_mx(osv.Model):
    _inherit = 'ir.attachment.facturae.mx'

    def _get_type(self, cr, uid, ids=None, context=None):
        if context is None:
            context = {}
        types = super(ir_attachment_facturae_mx, self)._get_type(
            cr, uid, ids, context=context)
        types.extend([
            ('cfdi32_pac_sf', 'CFDI 3.2 Solución Factible'),
        ])
        return types
    
    def get_driver_fc_sign(self):
        factura_mx_type__fc = super(ir_attachment_facturae_mx, self).get_driver_fc_sign()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi32_pac_sf': self._upload_ws_file})
        return factura_mx_type__fc
    
    def get_driver_fc_cancel(self):
        factura_mx_type__fc = super(ir_attachment_facturae_mx, self).get_driver_fc_cancel()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi32_pac_sf': self.sf_cancel})
        return factura_mx_type__fc
        
    _columns = {
        'type': fields.selection(_get_type, 'Type', type='char', size=64,
                                 required=True, readonly=True, help="Type of Electronic Invoice"),
    }
    
    def sf_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        msg = ''
        pac_params_obj = self.pool.get('params.pac')
        for attachment in self.browse(cr, uid, ids, context=context):
            status = False
            pac_params_ids = pac_params_obj.search(cr, uid, [
                ('method_type', '=', 'pac_sf_cancelar'),
                ('company_id', '=', attachment.company_id.id),
                ('active', '=', True),
            ], limit=1, context=context)
            pac_params_id = pac_params_ids and pac_params_ids[0] or False
            if pac_params_id:
                pac_params_brw = pac_params_obj.browse(
                    cr, uid, [pac_params_id], context=context)[0]
                user = pac_params_brw.user
                password = pac_params_brw.password
                wsdl_url = pac_params_brw.url_webservice
                namespace = pac_params_brw.namespace
                wsdl_client = False
                wsdl_client = WSDL.SOAPProxy(wsdl_url, namespace)
                fname_cer_no_pem = self.binary2file(cr, uid, ids,
                        attachment.certificate_file, 'openerp_' + '' + '__certificate__', '.cer')
                cerCSD = fname_cer_no_pem and base64.encodestring(
                    open(fname_cer_no_pem, "r").read()) or ''
                fname_key_no_pem = self.binary2file(cr, uid, ids,
                        attachment.certificate_key_file, 'openerp_' +'' + '__key__', '.key')
                keyCSD = fname_key_no_pem and base64.encodestring(
                    open(fname_key_no_pem, "r").read()) or ''
                zip = False  # Validar si es un comprimido zip, con la extension del archivo
                contrasenaCSD = attachment.certificate_password or ''
                uuids = attachment.cfdi_folio_fiscal  # cfdi_folio_fiscal
                params = [user, password, uuids, cerCSD, keyCSD, contrasenaCSD]
                wsdl_client.soapproxy.config.dumpSOAPOut = 0
                wsdl_client.soapproxy.config.dumpSOAPIn = 0
                wsdl_client.soapproxy.config.debug = 0
                wsdl_client.soapproxy.config.dict_encoding = 'UTF-8'
                result = wsdl_client.cancelar(*params)
                codigo_cancel = result['status'] or ''
                status_cancel = result['resultados'] and result['resultados']['status'] or ''
                uuid_nvo = result['resultados'] and result['resultados']['uuid'] or ''
                mensaje_cancel = _(tools.ustr(result['mensaje']))
                msg_nvo = result['resultados'] and result['resultados']['mensaje'] or ''
                status_uuid = result['resultados'] and result['resultados']['statusUUID'] or ''
                folio_cancel = result['resultados'] and result['resultados']['uuid'] or ''
                if codigo_cancel == '200' and status_cancel == '200' and status_uuid == '201':
                    msg +=  mensaje_cancel + _('\n- The process of cancellation\
                    has completed correctly.\n- The uuid cancelled is:\
                    ') + folio_cancel
                    attachment.write({
                        'cfdi_fecha_cancelacion': time.strftime(
                        '%Y-%m-%d %H:%M:%S')
                    })
                    status = True
                else:
                    raise orm.except_orm(_('Warning'), _('Cancel Code: %s.-Status code %s.-Status UUID: %s.-Folio Cancel: %s.-Cancel Message: %s.-Answer Message: %s.') % (
                        codigo_cancel, status_cancel, status_uuid, folio_cancel, mensaje_cancel, msg_nvo))
            else:
                msg = _('Not found information of webservices of PAC, verify that the configuration of PAC is correct')
        return {'message': msg, 'status_uuid': status_uuid, 'status': status}
    
    def _upload_ws_file(self, cr, uid, ids, fdata=None, context=None):
        """
        @params fdata : File.xml codification in base64
        """
        if context is None:
            context = {}
        pac_params_obj = self.pool.get('params.pac')
        for attachment in self.browse(cr, uid, ids, context=context):
            comprobante = 'cfdi:Comprobante'
            cfd_data = attachment.file_input_index
            xml_res_str = xml.dom.minidom.parseString(cfd_data.encode('ascii', 'xmlcharrefreplace'))
            xml_res_addenda = self.add_addenta_xml(
                cr, uid, xml_res_str, comprobante, context=context)
            xml_res_str_addenda = xml_res_addenda.toxml('UTF-8')
            xml_res_str_addenda = xml_res_str_addenda.replace(codecs.BOM_UTF8, '')
            
            if tools.config['test_report_directory']:#TODO: Add if test-enabled:
                ir_attach_facturae_mx_file_input = attachment.file_input and attachment.file_input or False
                fname_suffix = ir_attach_facturae_mx_file_input and ir_attach_facturae_mx_file_input.datas_fname or ''
                open( os.path.join(tools.config['test_report_directory'], 'l10n_mx_facturae_pac_sf' + '_' + \
                  'before_upload' + '-' + fname_suffix), 'wb+').write( xml_res_str_addenda )
            compr = xml_res_addenda.getElementsByTagName(comprobante)[0]
            date = compr.attributes['fecha'].value
            date_format = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
            context['date'] = date_format
            file = False
            msg = ''
            cfdi_xml = False
            status = False
            pac_params_ids = pac_params_obj.search(cr, uid, [
                ('method_type', '=', 'pac_sf_firmar'), (
                    'company_id', '=', attachment.company_id.id), (
                        'active', '=', True)], limit=1, context=context)
            if pac_params_ids:
                pac_params = pac_params_obj.browse(
                    cr, uid, pac_params_ids, context)[0]
                user = pac_params.user
                password = pac_params.password
                wsdl_url = pac_params.url_webservice
                namespace = pac_params.namespace
                certificate_link = pac_params.certificate_link
                url = 'https://solucionfactible.com/ws/services/Timbrado'
                testing_url = 'http://testing.solucionfactible.com/ws/services/Timbrado'
                if (wsdl_url == url) or (wsdl_url == testing_url):
                    pass
                else:
                    raise osv.except_osv(_('Warning'), _('Web Service URL \
                        o PAC incorrect'))
                if namespace == 'http://timbrado.ws.cfdi.solucionfactible.com':
                    pass
                else:
                    raise osv.except_osv(_('Warning'), _(
                        'Namespace of PAC incorrect'))
                if 'testing' in wsdl_url:
                    msg += _(u'WARNING, SIGNED IN TEST!!!!\n\n')
                wsdl_client = WSDL.SOAPProxy(wsdl_url, namespace)
                if True:  # if wsdl_client:
                    cfdi = base64.encodestring(xml_res_str_addenda)
                    zip = False  # Validar si es un comprimido zip, con la extension del archivo
                    contrasenaCSD = attachment.certificate_password or ''
                    params = [user, password, cfdi, zip]
                    wsdl_client.soapproxy.config.dumpSOAPOut = 0
                    wsdl_client.soapproxy.config.dumpSOAPIn = 0
                    wsdl_client.soapproxy.config.debug = 0
                    wsdl_client.soapproxy.config.dict_encoding = 'UTF-8'
                    resultado = wsdl_client.timbrar(*params)
                    htz = int(self._get_time_zone(cr, uid, ids, context=context))
                    mensaje = _(tools.ustr(resultado['mensaje']))
                    resultados_mensaje = resultado['resultados'] and \
                        resultado['resultados']['mensaje'] or ''
                    folio_fiscal = resultado['resultados'] and \
                        resultado['resultados']['uuid'] or ''
                    codigo_timbrado = resultado['status'] or ''
                    codigo_validacion = resultado['resultados'] and \
                        resultado['resultados']['status'] or ''
                    if codigo_timbrado == '311' or codigo_validacion == '311':
                        raise osv.except_osv(_('Warning'), _('Unauthorized.\nCode 311'))
                    elif codigo_timbrado == '312' or codigo_validacion == '312':
                        raise osv.except_osv(_('Warning'), _(
                            'Failed to consult the SAT.\nCode 312'))
                    elif codigo_timbrado == '200' and codigo_validacion == '200':
                        fecha_timbrado = resultado['resultados']['fechaTimbrado'] or False
                        fecha_timbrado = fecha_timbrado and time.strftime(
                            '%Y-%m-%d %H:%M:%S', time.strptime(
                                fecha_timbrado[:19], '%Y-%m-%dT%H:%M:%S')) or False
                        fecha_timbrado = fecha_timbrado and datetime.strptime(
                            fecha_timbrado, '%Y-%m-%d %H:%M:%S') + timedelta(
                                hours=htz) or False
                        cfdi_data = {
                            #'cfdi_cbb': resultado['resultados']['qrCode'] or False,  # ya lo regresa en base64
                            'cfdi_sello': resultado['resultados'][
                            'selloSAT'] or False,
                            'cfdi_no_certificado': resultado['resultados'][
                            'certificadoSAT'] or False,
                            'cfdi_cadena_original': resultado['resultados'][
                            'cadenaOriginal'] or False,
                            'cfdi_fecha_timbrado': fecha_timbrado,
                            'cfdi_xml': base64.decodestring(resultado[
                            'resultados']['cfdiTimbrado'] or ''),  # este se necesita en uno que no es base64
                            'cfdi_folio_fiscal': resultado['resultados']['uuid'] or '',
                            'pac_id': pac_params.id,
                            'certificate_link': certificate_link or False,
                        }
                        msg += mensaje + "." + resultados_mensaje + \
                            " Folio Fiscal: " + folio_fiscal + "."
                        msg += _(
                                u"\nMake Sure to the file really has generated correctly to the SAT\nhttps://www.consulta.sat.gob.mx/sicofi_web/moduloECFD_plus/ValidadorCFDI/Validador%20cfdi.html")
                        if cfdi_data.get('cfdi_xml', False):
                            url_pac = '</"%s"><!--Para validar el XML CFDI puede descargar el certificado del PAC desde la siguiente liga: https://solucionfactible.com/cfdi/00001000000102699425.zip-->' % (
                                comprobante)
                            cfdi_data['cfdi_xml'] = cfdi_data[
                                'cfdi_xml'].replace('</"%s">' % (comprobante), url_pac)
                            file = base64.encodestring(
                                cfdi_data['cfdi_xml'] or '')
                            cfdi_xml = cfdi_data.pop('cfdi_xml')
                        if cfdi_xml:
                            attachment.write(cfdi_data)
                            cfdi_data['cfdi_xml'] = cfdi_xml
                            status = True
                        else:
                            msg += _(u"Can't extract the file XML of PAC")
                    else:
                        raise orm.except_orm(_('Warning'), _('Stamped Code: %s.-Validation code %s.-Folio Fiscal: %s.-Stamped Message: %s.-Validation Message: %s.') % (
                            codigo_timbrado, codigo_validacion, folio_fiscal, mensaje, resultados_mensaje))
            else:
                msg += 'Not found information from web services of PAC, verify that the configuration of PAC is correct'
                raise osv.except_osv(_('Warning'), _(
                    'Not found information from web services of PAC, verify that the configuration of PAC is correct'))
            return {'file': file, 'msg': msg, 'cfdi_xml': cfdi_xml, 'status': status}
            
    def add_node(self, node_name=None, attrs=None, parent_node=None,
                 minidom_xml_obj=None, attrs_types=None, order=False):
        """
            @params node_name : Name node to added
            @params attrs : Attributes to add in node
            @params parent_node : Node parent where was add new node children
            @params minidom_xml_obj : File XML where add nodes
            @params attrs_types : Type of attributes added in the node
            @params order : If need add the params in order in the XML, add a
                    list with order to params
        """
        if not order:
            order = attrs
        new_node = minidom_xml_obj.createElement(node_name)
        for key in order:
            if attrs_types[key] == 'attribute':
                new_node.setAttribute(key, attrs[key])
            elif attrs_types[key] == 'textNode':
                key_node = minidom_xml_obj.createElement(key)
                text_node = minidom_xml_obj.createTextNode(attrs[key])

                key_node.appendChild(text_node)
                new_node.appendChild(key_node)
        parent_node.appendChild(new_node)
        return new_node

    def add_addenta_xml(self, cr, ids, xml_res_str=None, comprobante=None, context=None):
        """
         @params xml_res_str : File XML
         @params comprobante : Name to the Node that contain the information the XML
        """
        if context is None:
            context = {}
        if xml_res_str:
            node_Addenda = xml_res_str.getElementsByTagName('cfdi:Addenda')
            if len(node_Addenda) == 0:
                nodeComprobante = xml_res_str.getElementsByTagName(
                    comprobante)[0]
                node_Addenda = self.add_node(
                    'cfdi:Addenda', {}, nodeComprobante, xml_res_str, attrs_types={})
                node_Partner_attrs = {
                    'xmlns:sf': "http://timbrado.solucionfactible.com/partners",
                    'xsi:schemaLocation': "http://timbrado.solucionfactible.com/partners https://solucionfactible.com/timbrado/partners/partners.xsd",
                    'id': "150731"
                }
                node_Partner_attrs_types = {
                    'xmlns:sf': 'attribute',
                    'xsi:schemaLocation': 'attribute',
                    'id': 'attribute'
                }
                node_Partner = self.add_node('sf:Partner', node_Partner_attrs,
                                             node_Addenda, xml_res_str, attrs_types=node_Partner_attrs_types)
            else:
                node_Partner_attrs = {
                    'xmlns:sf': "http://timbrado.solucionfactible.com/partners",
                    'xsi:schemaLocation': "http://timbrado.solucionfactible.com/partners https://solucionfactible.com/timbrado/partners/partners.xsd",
                    'id': "150731"
                }
                node_Partner_attrs_types = {
                    'xmlns:sf': 'attribute',
                    'xsi:schemaLocation': 'attribute',
                    'id': 'attribute'
                }
                node_Partner = self.add_node('sf:Partner', node_Partner_attrs,
                                             node_Addenda, xml_res_str, attrs_types=node_Partner_attrs_types)
        return xml_res_str

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
