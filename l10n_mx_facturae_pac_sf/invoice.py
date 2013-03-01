# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Financed by: http://www.sfsoluciones.com (aef@sfsoluciones.com)
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
from openerp.osv import osv, fields
import base64
import xml.dom.minidom

import wizard
import netsvc
import time
import base64
import StringIO
import csv
import tempfile
import os
import sys
import codecs
import xml.dom.minidom
from datetime import datetime, timedelta
from tools.misc import ustr
try:
    from SOAPpy import WSDL
except:
    print "Package SOAPpy missed"
    pass
import time

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    _columns = {
        'cfdi_cbb': fields.binary('CFD-I CBB'),
        'cfdi_sello': fields.text('CFD-I Sello'),
        'cfdi_no_certificado': fields.char('CFD-I Certificado', size=32),
        'cfdi_cadena_original': fields.text('CFD-I Cadena Original'),
        'cfdi_fecha_timbrado': fields.datetime('CFD-I Fecha Timbrado'),
        'cfdi_fecha_cancelacion': fields.datetime('CFD-I Fecha Cancelacion'),
        'cfdi_folio_fiscal': fields.char('CFD-I Folio Fiscal', size=64),
    }

    def cfdi_data_write(self, cr, uid, ids, cfdi_data, context={}):
        if not context:
            context = {}
        attachment_obj = self.pool.get('ir.attachment')
        cfdi_xml = cfdi_data.pop('cfdi_xml')
        if cfdi_xml:
            self.write(cr, uid, ids, cfdi_data)
            cfdi_data['cfdi_xml'] = cfdi_xml # Regresando valor, despues de hacer el write normal
            """for invoice in self.browse(cr, uid, ids):
                #fname, xml_data = self.pool.get('account.invoice')._get_facturae_invoice_xml_data(cr, uid, [inv.id], context=context)
                fname_invoice = invoice.fname_invoice and invoice.fname_invoice + '.xml' or ''
                data_attach = {
                    'name': fname_invoice,
                    'datas': base64.encodestring( cfdi_xml or '') or False,
                    'datas_fname': fname_invoice,
                    'description': 'Factura-E XML CFD-I',
                    'res_model': 'account.invoice',
                    'res_id': invoice.id,
                }
                attachment_ids = attachment_obj.search(cr, uid, [('name','=',fname_invoice),('res_model','=','account.invoice'),('res_id', '=', invoice.id)])
                if attachment_ids:
                    attachment_obj.write(cr, uid, attachment_ids, data_attach, context=context)
                else:
                    attachment_obj.create(cr, uid, data_attach, context=context)
                """
        return True

    def copy(self, cr, uid, id, default={}, context=None):
        if context is None:
            context = {}
        default.update({
            'cfdi_cbb': False,
            'cfdi_sello':False,
            'cfdi_no_certificado':False,
            'cfdi_cadena_original':False,
            'cfdi_fecha_timbrado': False,
            'cfdi_folio_fiscal': False,
            'cfdi_fecha_cancelacion': False,
        })
        return super(account_invoice, self).copy(cr, uid, id, default, context)
    """
    TODO: reset to draft considerated to delete these fields?
    def action_cancel_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {
            'cfdi_cbb': False,
            'cfdi_sello':False,
            'cfdi_no_certificado':False,
            'cfdi_cadena_original':False,
            'cfdi_fecha_timbrado': False,
            'cfdi_folio_fiscal': False,
            'cfdi_fecha_cancelacion': False,
        })
        return super(account_invoice, self).action_cancel_draft(cr, uid, ids, args)
    """

    def _get_file(self, cr, uid, inv_ids , context={}):
        if not context:
            context = {}
        id = inv_ids[0]
        invoice = self.browse(cr, uid, [id], context=context)[0]
        fname_invoice = invoice.fname_invoice and invoice.fname_invoice + '.xml' or ''
        aids = self.pool.get('ir.attachment').search(cr, uid, [('datas_fname','=',invoice.fname_invoice+'.xml'),('res_model','=','account.invoice'),('res_id','=',id)])
        xml_data = ""
        if aids:
            brow_rec = self.pool.get('ir.attachment').browse(cr, uid, aids[0])
            if brow_rec.datas:
                xml_data = base64.decodestring(brow_rec.datas)
        else:
            fname, xml_data = self._get_facturae_invoice_xml_data(cr, uid, inv_ids, context=context)
            self.pool.get('ir.attachment').create(cr, uid, {
                    'name': fname_invoice,
                    'datas': base64.encodestring(xml_data),
                    'datas_fname': fname_invoice,
                    'res_model': 'account.invoice',
                    'res_id': invoice.id,
                }, context=context)
        self.fdata = base64.encodestring( xml_data )
        msg = "Presiona clic en el boton 'subir archivo'"
        return {'file': self.fdata, 'fname': fname_invoice, 'name': fname_invoice, 'msg': msg}
        
    def add_node(self, node_name, attrs, parent_node, minidom_xml_obj, attrs_types,order=False):
        if not order:
            order=attrs
        new_node = minidom_xml_obj.createElement(node_name)
        for key in order:
            if attrs_types[key] == 'attribute':
                new_node.setAttribute(key, attrs[key])
            elif attrs_types[key] == 'textNode':
                key_node = minidom_xml_obj.createElement( key )
                text_node = minidom_xml_obj.createTextNode( attrs[key] )
                
                key_node.appendChild( text_node )
                new_node.appendChild( key_node )
        parent_node.appendChild( new_node )
        return new_node
        
    def add_addenta_xml(self, cr, ids, xml_res_str=None, comprobante=None, context={}):
        if xml_res_str:
            node_Addenda = xml_res_str.getElementsByTagName('Addenda')
            if len(node_Addenda) == 0:
                nodeComprobante = xml_res_str.getElementsByTagName(comprobante)[0]
                node_Addenda = self.add_node('Addenda', {}, nodeComprobante, xml_res_str, attrs_types={})
                node_Partner_attrs = {
                    'xmlns:sf' : "http://timbrado.solucionfactible.com/partners",
                    'xsi:schemaLocation' : "http://timbrado.solucionfactible.com/partners https://solucionfactible.com/timbrado/partners/partners.xsd",
                    'id' : "150731"
                }
                node_Partner_attrs_types = {
                    'xmlns:sf' : 'attribute',
                    'xsi:schemaLocation' : 'attribute',
                    'id' : 'attribute'
                }
                node_Partner = self.add_node('sf:Partner', node_Partner_attrs, node_Addenda, xml_res_str, attrs_types=node_Partner_attrs_types)
            else:
                node_Partner_attrs = {
                    'xmlns:sf' : "http://timbrado.solucionfactible.com/partners",
                    'xsi:schemaLocation' : "http://timbrado.solucionfactible.com/partners https://solucionfactible.com/timbrado/partners/partners.xsd",
                    'id' : "150731"
                }
                node_Partner_attrs_types = {
                    'xmlns:sf' : 'attribute',
                    'xsi:schemaLocation' : 'attribute',
                    'id' : 'attribute'
                }
                node_Partner = self.add_node('sf:Partner', node_Partner_attrs, node_Addenda, xml_res_str, attrs_types=node_Partner_attrs_types)
        return xml_res_str
        
    def _upload_ws_file(self, cr, uid, inv_ids, fdata=None, context={}):
        ir_seq_app_obj = self.pool.get('ir.sequence.approval')
        invoice = self.browse(cr, uid, inv_ids[0], context=context)
        sequence_app_id = ir_seq_app_obj.search(cr, uid, [('sequence_id', '=', invoice.invoice_sequence_id.id)], context=context)
        type_inv = 'cfd22'
        if sequence_app_id:
            type_inv = ir_seq_app_obj.browse(cr, uid, sequence_app_id[0], context=context).type
        if type_inv == 'cfdi32':
            comprobante = 'cfdi:Comprobante'
        else:
            comprobante = 'Comprobante'
        pac_params_obj = self.pool.get('params.pac')
        cfd_data = base64.decodestring( fdata or self.fdata )
        xml_res_str = xml.dom.minidom.parseString(cfd_data)
        xml_res_addenda = self.add_addenta_xml(cr, uid, xml_res_str, comprobante, context=context)
        xml_res_str_addenda = xml_res_addenda.toxml('UTF-8')
        compr = xml_res_addenda.getElementsByTagName(comprobante)[0]
        date = compr.attributes['fecha'].value
        date_format = datetime.strptime( date, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
        context['date']=date_format
        invoice_ids = inv_ids
        invoice = self.browse(cr, uid, invoice_ids, context=context)[0]
        currency = invoice.currency_id.name
        currency_enc = currency.encode('UTF-8', 'strict')
        rate = invoice.currency_id.rate and (1.0/invoice.currency_id.rate) or 1
        file = False
        msg = ''
        status = ''
        cfdi_xml = False
        pac_params_ids = pac_params_obj.search(cr,uid,[('method_type','=','pac_sf_firmar'), ('company_id', '=', invoice.company_emitter_id.id), ('active', '=', True)], limit=1, context=context)
        if pac_params_ids:
            pac_params = pac_params_obj.browse(cr, uid, pac_params_ids, context)[0]
            user = pac_params.user
            password = pac_params.password
            wsdl_url = pac_params.url_webservice
            namespace = pac_params.namespace
            if 'testing' in wsdl_url:
                msg += u'CUIDADO FIRMADO EN PRUEBAS!!!!\n\n'
            wsdl_client = WSDL.SOAPProxy( wsdl_url, namespace )
            if True:#if wsdl_client:
                file_globals = self._get_file_globals(cr, uid, invoice_ids, context=context)
                fname_cer_no_pem = file_globals['fname_cer']
                cerCSD = fname_cer_no_pem and base64.encodestring( open(fname_cer_no_pem, "r" ).read() ) or ''
                fname_key_no_pem = file_globals['fname_key']
                keyCSD = fname_key_no_pem and base64.encodestring( open(fname_key_no_pem, "r" ).read() ) or ''
                cfdi = base64.encodestring( xml_res_str_addenda.replace(codecs.BOM_UTF8,'') )
                zip = False#Validar si es un comprimido zip, con la extension del archivo
                contrasenaCSD = file_globals.get('password', '')
                params = [user, password, cfdi, cerCSD, keyCSD, contrasenaCSD, zip]
                wsdl_client.soapproxy.config.dumpSOAPOut = 0
                wsdl_client.soapproxy.config.dumpSOAPIn = 0
                wsdl_client.soapproxy.config.debug = 0
                wsdl_client.soapproxy.config.dict_encoding='UTF-8'
                resultado = wsdl_client.timbrar(*params)
                msg += resultado['resultados'] and resultado['resultados']['mensaje'] or ''
                status = resultado['resultados'] and resultado['resultados']['status'] or ''
                if status == '200' or status == '307':
                    fecha_timbrado = resultado['resultados']['fechaTimbrado'] or False
                    fecha_timbrado = fecha_timbrado and time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(fecha_timbrado[:19], '%Y-%m-%dT%H:%M:%S')) or False
                    fecha_timbrado = fecha_timbrado and datetime.strptime(fecha_timbrado, '%Y-%m-%d %H:%M:%S') + timedelta(hours=-6) or False
                    cfdi_data = {
                        'cfdi_cbb': resultado['resultados']['qrCode'] or False,#ya lo regresa en base64
                        'cfdi_sello': resultado['resultados']['selloSAT'] or False,
                        'cfdi_no_certificado': resultado['resultados']['certificadoSAT'] or False,
                        'cfdi_cadena_original': resultado['resultados']['cadenaOriginal'] or False,
                        'cfdi_fecha_timbrado': fecha_timbrado,
                        'cfdi_xml': base64.decodestring( resultado['resultados']['cfdiTimbrado'] or '' ),#este se necesita en uno que no es base64
                        'cfdi_folio_fiscal': resultado['resultados']['uuid'] or '' ,
                    }
                    if cfdi_data.get('cfdi_xml', False):
                        url_pac = '</"%s"><!--Para validar el XML CFDI puede descargar el certificado del PAC desde la siguiente liga: https://solucionfactible.com/cfdi/00001000000102699425.zip-->'%(comprobante)
                        cfdi_data['cfdi_xml'] = cfdi_data['cfdi_xml'].replace('</"%s">'%(comprobante), url_pac)
                        file = base64.encodestring( cfdi_data['cfdi_xml'] or '' )
                        #self.cfdi_data_write(cr, uid, [invoice.id], cfdi_data, context=context)
                        cfdi_xml = cfdi_data.pop('cfdi_xml')
                        if cfdi_xml:
                            self.write(cr, uid, inv_ids, cfdi_data)
                            cfdi_data['cfdi_xml'] = cfdi_xml
                        msg = msg + "\nAsegurese de que su archivo realmente haya sido generado correctamente ante el SAT\nhttps://www.consulta.sat.gob.mx/sicofi_web/moduloECFD_plus/ValidadorCFDI/Validador%20cfdi.html"
                    else:
                        msg = msg + "\nNo se pudo extraer el archivo XML del PAC"
                elif status == '500' or status == '307':#documento no es un cfd version 2, probablemente ya es un CFD version 3
                    msg = "Probablemente el archivo XML ya ha sido timbrado previamente y no es necesario volverlo a subir.\nO puede ser que el formato del archivo, no es el correcto.\nPor favor, visualice el archivo para corroborarlo y seguir con el siguiente paso o comuniquese con su administrador del sistema.\n" + ( resultado['resultados']['mensaje'] or '') + ( resultado['mensaje'] or '' )
                else:
                    msg += '\n' + resultado['mensaje'] or ''
                    if not status:
                        status = 'parent_' + resultado['status']
        else:
            msg = 'No se encontro informacion del webservices del PAC, verifique que la configuración del PAC sea correcta'
        return {'file': file, 'msg': msg, 'status': status, 'cfdi_xml': cfdi_xml }
        
    def _get_file_cancel(self, cr, uid, inv_ids, context = {}):
        inv_ids = inv_ids[0]
        atta_obj = self.pool.get('ir.attachment')
        atta_id = atta_obj.search(cr, uid, [('res_id', '=', inv_ids), ('name', 'ilike', '%.xml')], context=context)
        res={}
        if atta_id:
            atta_brw = atta_obj.browse(cr, uid, atta_id, context)[0]
            inv_xml = atta_brw.datas or False
        else:
            inv_xml = False
            raise osv.except_osv(('Estado de Cancelación!'),('Esta factura no ha sido timbrada, por lo que no es posible cancelarse.'))
        return {'file': inv_xml}

    def sf_cancel(self, cr, uid, inv_ids, context=None):
        context_id=inv_ids[0]
        company_obj = self.pool.get('res.company.facturae.certificate')
        pac_params_obj = self.pool.get('params.pac')

        invoice_brw = self.browse(cr, uid, context_id, context)
        company_brw = company_obj.browse(cr, uid, [invoice_brw.company_id.id], context)[0]
        pac_params_srch = pac_params_obj.search(cr,uid,[('method_type','=','pac_sf_cancelar'), ('company_id', '=', invoice_brw.company_emitter_id.id), ('active', '=', True)], context=context)

        if pac_params_srch:
            pac_params_brw = pac_params_obj.browse(cr, uid, pac_params_srch, context)[0]
            user = pac_params_brw.user
            password = pac_params_brw.password
            wsdl_url = pac_params_brw.url_webservice
            namespace = pac_params_brw.namespace
            #---------constantes
            #~ user = 'testing@solucionfactible.com'
            #~ password = 'timbrado.SF.16672'
            #~ wsdl_url = 'http://testing.solucionfactible.com/ws/services/Timbrado?wsdl'
            #~ namespace = 'http://timbrado.ws.cfdi.solucionfactible.com'

            wsdl_client = False
            wsdl_client = WSDL.SOAPProxy( wsdl_url, namespace )
            if True:#if wsdl_client:
                file_globals = self._get_file_globals(cr, uid, [context_id], context=context)
                fname_cer_no_pem = file_globals['fname_cer']
                cerCSD = fname_cer_no_pem and base64.encodestring( open(fname_cer_no_pem, "r" ).read() ) or ''
                fname_key_no_pem = file_globals['fname_key']
                keyCSD = fname_key_no_pem and base64.encodestring( open(fname_key_no_pem, "r" ).read() ) or ''
                zip = False#Validar si es un comprimido zip, con la extension del archivo
                contrasenaCSD = file_globals.get('password', '')
                uuids = invoice_brw.cfdi_folio_fiscal#cfdi_folio_fiscal

                params = [user, password, uuids, cerCSD, keyCSD, contrasenaCSD ]
                wsdl_client.soapproxy.config.dumpSOAPOut = 0
                wsdl_client.soapproxy.config.dumpSOAPIn = 0
                wsdl_client.soapproxy.config.debug = 0
                wsdl_client.soapproxy.config.dict_encoding='UTF-8'
                result = wsdl_client.cancelar(*params)

                status = result['resultados'] and result['resultados']['status'] or ''
                #agregados
                uuid_nvo = result['resultados'] and result['resultados']['uuid'] or ''
                msg_nvo = result['resultados'] and result['resultados']['mensaje'] or ''

                status_uuid = result['resultados'] and result['resultados']['statusUUID'] or ''
                msg_status={}
                if status =='200':
                    folio_cancel = result['resultados'] and result['resultados']['uuid'] or ''
                    msg_global = '\n- El proceso de cancelación se ha completado correctamente.\n- El uuid cancelado es: ' + folio_cancel+'\n\nMensaje Técnico:\n'
                    msg_tecnical = 'Status:',status,' uuid:',uuid_nvo,' msg:',msg_nvo,'Status uuid:',status_uuid
                else:
                    msg_global = '\n- Han ocurrido errores que no han permitido completar el proceso de cancelación, asegurese de que la factura que intenta cancelar ha sido timbrada previamente.\n\nMensaje Técnico:\n'
                    msg_tecnical = 'status:',status,' uuidnvo:',uuid_nvo,' MENSJAE:NVO',msg_nvo,'STATUS UUID:',status_uuid

                if status_uuid == '201':
                    msg_SAT = '- Estatus de respuesta del SAT: 201. El folio se ha cancelado con éxito.'
                    self.write(cr, uid, context_id, {'cfdi_fecha_cancelacion':time.strftime('%Y-%m-%d %H:%M:%S')})
                elif status_uuid == '202':
                    msg_SAT = '- Estatus de respuesta del SAT: 202. El folio ya se había cancelado previamente.'
                elif status_uuid == '203':
                    msg_SAT = '- Estatus de respuesta del SAT: 203. El comprobante que intenta cancelar no corresponde al contribuyente con el que se ha firmado la solicitud de cancelación.'
                elif status_uuid == '204':
                    msg_SAT = '- Estatus de respuesta del SAT: 204. El CFDI no aplica para cancelación.'
                elif status_uuid == '205':
                    msg_SAT = '- Estatus de respuesta del SAT: 205. No se encuentra el folio del CFDI para su cancelación.'
                else:
                    msg_SAT = '- Estatus de respuesta del SAT desconocido'
                msg_global = msg_SAT + msg_global  + str(msg_tecnical)
        else:
            msg_global='No se encontro información del webservices del PAC, verifique que la configuración del PAC sea correcta'
        return {'message': msg_global }

account_invoice()
