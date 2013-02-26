# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t260@vauxoo.com)
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
import tempfile
import os
import codecs
import base64
import xml.dom.minidom
from datetime import datetime, timedelta
try:
    from SOAPpy import WSDL
except:
    print "Package SOAPpy missed"
    pass
import time

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def _get_facturae_invoice_dict_data(self, cr, uid, ids, context={}):
        datas = super(account_invoice, self)._get_facturae_invoice_dict_data(cr, uid, ids, context=context)
        ir_seq_app_obj = self.pool.get('ir.sequence.approval')
        invoice = self.browse(cr, uid, ids[0], context=context)
        sequence_app_id = ir_seq_app_obj.search(cr, uid, [('sequence_id', '=', invoice.invoice_sequence_id.id)], context=context)
        type_inv = 'cfd22'
        if sequence_app_id:
            type_inv = ir_seq_app_obj.browse(cr, uid, sequence_app_id[0], context=context).type
        for data in datas:
            if type_inv == 'cfdi32':
                comprobante = data['Comprobante']
                rfc = comprobante['Emisor']['rfc']
                nombre = comprobante['Emisor']['nombre']
                dom_Fiscal = comprobante['Emisor']['DomicilioFiscal']
                exp_en = comprobante['Emisor']['ExpedidoEn']
                reg_Fiscal = comprobante['Emisor']['RegimenFiscal']
                rfc_receptor = comprobante['Receptor']['rfc']
                nombre_receptor = comprobante['Receptor']['nombre']
                domicilio_receptor = comprobante['Receptor']['Domicilio']
                totalImpuestosTrasladados = comprobante['Impuestos']['totalImpuestosTrasladados']
                dict_cfdi_comprobante = {}
                dict_emisor = dict({'rfc' : rfc, 'nombre' : nombre, 'cfdi:DomicilioFiscal' : dom_Fiscal, 'cfdi:ExpedidoEn' : exp_en, 'cfdi:RegimenFiscal' : reg_Fiscal})
                dict_receptor = dict({'rfc' : rfc_receptor, 'nombre' : nombre_receptor, 'cfdi:Domicilio' : domicilio_receptor})
                list_conceptos = []
                dict_impuestos = dict({'totalImpuestosTrasladados' : totalImpuestosTrasladados, 'cfdi:Traslados' : []})
                for concepto in comprobante['Conceptos']:
                    list_conceptos.append(dict({'cfdi:Concepto' : concepto['Concepto']}))
                for traslado in comprobante['Impuestos']['Traslados']:
                    dict_impuestos['cfdi:Traslados'].append(dict({'cfdi:Traslado' : traslado['Traslado']}))
                comprobante.update({'cfdi:Emisor' : dict_emisor, 
                                    'cfdi:Receptor' : dict_receptor,
                                    'cfdi:Conceptos' : list_conceptos,
                                    'cfdi:Impuestos' : dict_impuestos,
                    })
                comprobante.pop('Emisor')
                comprobante.pop('Impuestos')
                comprobante.pop('Conceptos')
                comprobante.pop('Receptor')
                comprobante.pop('xsi:schemaLocation')
                comprobante.update({'xmlns:cfdi' : "http://www.sat.gob.mx/cfd/3", 'xsi:schemaLocation': "http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv32.xsd", 'version': "3.2",})
                comprobante.pop('xmlns')
                dict_comprobante = comprobante
                data.pop('Comprobante')
                data.update(dict({'cfdi:Comprobante' : dict_comprobante}))
        return datas
        
    def _get_facturae_invoice_xml_data(self, cr, uid, ids, context={}):
        if not context:
            context = {}
        ir_seq_app_obj = self.pool.get('ir.sequence.approval')
        invoice = self.browse(cr, uid, ids[0], context=context)
        sequence_app_id = ir_seq_app_obj.search(cr, uid, [('sequence_id', '=', invoice.invoice_sequence_id.id)], context=context)
        type_inv = 'cfd22'
        if sequence_app_id:
            type_inv = ir_seq_app_obj.browse(cr, uid, sequence_app_id[0], context=context).type
        if type_inv == 'cfdi32':
            comprobante = 'cfdi:Comprobante'
            emisor = 'cfdi:Emisor'
        else:
            comprobante = 'Comprobante'
            emisor = 'Emisor'
        data_dict = self._get_facturae_invoice_dict_data(cr, uid, ids, context=context)[0]
        doc_xml = self.dict2xml( {comprobante : data_dict.get(comprobante) } )
        invoice_number = "sn"
        (fileno_xml, fname_xml) = tempfile.mkstemp('.xml', 'openerp_' + (invoice_number or '') + '__facturae__' )
        fname_txt =  fname_xml + '.txt'
        f = open(fname_xml, 'w')
        doc_xml.writexml(f, indent='    ', addindent='    ', newl='\r\n', encoding='UTF-8')
        f.close()
        os.close(fileno_xml)

        (fileno_sign, fname_sign) = tempfile.mkstemp('.txt', 'openerp_' + (invoice_number or '') + '__facturae_txt_md5__' )
        os.close(fileno_sign)

        context.update({
            'fname_xml': fname_xml,
            'fname_txt': fname_txt,
            'fname_sign': fname_sign,
        })
        context.update( self._get_file_globals(cr, uid, ids, context=context) )
        fname_txt, txt_str = self._xml2cad_orig(cr=False, uid=False, ids=False, context=context)
        data_dict['cadena_original'] = txt_str

        if not txt_str:
            raise osv.except_osv(_('Error en Cadena original!'), _('No se pudo obtener la cadena original del comprobante.\nVerifique su configuracion.\n%s'%(msg2)) )

        if not data_dict[comprobante].get('folio', ''):
            raise osv.except_osv(_('Error en Folio!'), _('No se pudo obtener el Folio del comprobante.\nAntes de generar el XML, de clic en el boton, generar factura.\nVerifique su configuracion.\n%s'%(msg2)) )

        context.update( { 'fecha': data_dict[comprobante]['fecha'] } )
        sign_str = self._get_sello(cr=False, uid=False, ids=False, context=context)
        if not sign_str:
            raise osv.except_osv(_('Error en Sello !'), _('No se pudo generar el sello del comprobante.\nVerifique su configuracion.\ns%s')%(msg2))

        nodeComprobante = doc_xml.getElementsByTagName(comprobante)[0]
        nodeComprobante.setAttribute("sello", sign_str)
        data_dict[comprobante]['sello'] = sign_str

        noCertificado = self._get_noCertificado( context['fname_cer'] )
        if not noCertificado:
            raise osv.except_osv(_('Error en No Certificado !'), _('No se pudo obtener el No de Certificado del comprobante.\nVerifique su configuracion.\n%s')%(msg2))
        nodeComprobante.setAttribute("noCertificado", noCertificado)
        data_dict[comprobante]['noCertificado'] = noCertificado

        cert_str = self._get_certificate_str( context['fname_cer'] )
        if not cert_str:
            raise osv.except_osv(_('Error en Certificado!'), _('No se pudo generar el Certificado del comprobante.\nVerifique su configuracion.\n%s')%(msg2))
        cert_str = cert_str.replace(' ', '').replace('\n', '')
        nodeComprobante.setAttribute("certificado", cert_str)
        data_dict[comprobante]['certificado'] = cert_str

        self.write_cfd_data(cr, uid, ids, data_dict, context=context)

        if context.get('type_data') == 'dict':
            return data_dict
        if context.get('type_data') == 'xml_obj':
            return doc_xml
        data_xml = doc_xml.toxml('UTF-8')
        data_xml = codecs.BOM_UTF8 + data_xml
        fname_xml = (data_dict[comprobante][emisor]['rfc'] or '') + '.' + ( data_dict[comprobante].get('serie', '') or '') + '.' + ( data_dict[comprobante].get('folio', '') or '') + '.xml'
        data_xml = data_xml.replace ('<?xml version="1.0" encoding="UTF-8"?>','<?xml version="1.0" encoding="UTF-8"?>\n')
        return fname_xml, data_xml
        
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
        compr = xml_res_str.getElementsByTagName(comprobante)[0]
        date = compr.attributes['fecha'].value
        date_format = datetime.strptime( date, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
        context['date']=date_format
        invoice_ids = inv_ids
        invoice = self.browse(cr, uid, invoice_ids, context=context)[0]
        currency = invoice.currency_id.name
        currency_enc = currency.encode('UTF-8', 'strict')
        rate = invoice.currency_id.rate and (1.0/invoice.currency_id.rate) or 1
        moneda = '''<Addenda>
            <xmlns:sferp="http://www.solucionfactible.com/cfd/divisas" xsi:schemaLocation="http://www.solucionfactible.com/cfd/divisas http://solucionfactible.com/addenda/divisas.xsd"/>
            <sf:Partner xmlns:sf="http://timbrado.solucionfactible.com/partners" xsi:schemaLocation="http://timbrado.solucionfactible.com/partners https://solucionfactible.com/timbrado/partners/partners.xsd" id="150731"/>
        </Addenda> </cfdi:Comprobante>'''
        file = False
        msg = ''
        status = ''
        cfdi_xml = False

        cfd_data_adenda = cfd_data.replace('</Comprobante>', moneda)
        pac_params_ids = pac_params_obj.search(cr,uid,[('method_type','=','pac_sf_firmar'), ('company_id', '=', invoice.company_emitter_id.id), ('active', '=', True)], limit=1, context=context)

        if pac_params_ids:
            pac_params = pac_params_obj.browse(cr, uid, pac_params_ids, context)[0]
            user = pac_params.user
            password = pac_params.password
            wsdl_url = pac_params.url_webservice
            namespace = pac_params.namespace
            if 'testing' in wsdl_url:
                msg += u'CUIDADO FIRMADO EN PRUEBAS!!!!\n\n'
            if cfd_data_adenda:

                wsdl_client = WSDL.SOAPProxy( wsdl_url, namespace )
                if True:#if wsdl_client:

                    file_globals = self._get_file_globals(cr, uid, invoice_ids, context=context)
                    fname_cer_no_pem = file_globals['fname_cer']
                    cerCSD = fname_cer_no_pem and base64.encodestring( open(fname_cer_no_pem, "r" ).read() ) or ''
                    fname_key_no_pem = file_globals['fname_key']
                    keyCSD = fname_key_no_pem and base64.encodestring( open(fname_key_no_pem, "r" ).read() ) or ''
                    cfdi = base64.encodestring( cfd_data_adenda.replace(codecs.BOM_UTF8,'') )
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
                            url_pac = '</cfdi:Comprobante><!--Para validar el XML CFDI puede descargar el certificado del PAC desde la siguiente liga: https://solucionfactible.com/cfdi/00001000000102699425.zip-->'
                            cfdi_data['cfdi_xml'] = cfdi_data['cfdi_xml'].replace('</cfdi:Comprobante>', url_pac)
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
            
account_invoice()
