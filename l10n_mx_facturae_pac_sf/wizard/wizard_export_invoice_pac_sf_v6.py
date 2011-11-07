# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info moylop260 (moylop260@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Coded by: isaac (isaac@vauxoo.com)
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

from osv import fields, osv
import wizard
import netsvc
import pooler
import time
import base64
import StringIO
import csv
import tempfile
import os
import sys
import codecs
from tools.misc import ustr
try:
    from SOAPpy import WSDL
except:
    print "Package SOAPpy missed"
    pass
import time


class wizard_export_invoice_pac_sf_v6(osv.osv_memory):
    _name='wizard.export.invoice.pac.sf.v6'

    def inicia(self, cr, uid, context=None):
       print 'entro de inicia'
       return 'nada'


    def _get_file(self, cr, uid, data, context={}):
        print 'dentro del _get_file el data es',data
        if not context:
            context = {}
        #context.update( {'date': data['form']['date']} )
        pool = pooler.get_pool(cr.dbname)
        invoice_obj = pool.get('account.invoice')
        ids = data['active_ids']
        id = ids[0]
        invoice = invoice_obj.browse(cr, uid, [id], context=context)[0]
        fname_invoice = invoice.fname_invoice and invoice.fname_invoice + '.xml' or ''
        aids = pool.get('ir.attachment').search(cr, uid, [('datas_fname','=',invoice.fname_invoice+'.xml'),('res_model','=','account.invoice'),('res_id','=',id)])
        xml_data = ""
        if aids:
            brow_rec = pool.get('ir.attachment').browse(cr, uid, aids[0])
            if brow_rec.datas:
                xml_data = base64.decodestring(brow_rec.datas)
        else:
            fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(cr, uid, ids, context=context)
            pool.get('ir.attachment').create(cr, uid, {
                    'name': fname_invoice,
                    'datas': base64.encodestring(xml_data),
                    'datas_fname': fname_invoice,
                    'res_model': 'account.invoice',
                    'res_id': invoice.id,
                }, context=context)

        fdata = base64.encodestring( xml_data )
        msg = "Presiona clic en el boton 'subir archivo'"
        #~ return {'file': fdata, 'fname': fname_invoice, 'msg': msg}
        self.fdata=fdata
        self.msg=msg
        self.fdata=fdata
        self.id=id
        return fdata
        #~ return {'file': fdata, 'fname': fname_invoice, 'msg': msg}

    def upload_ws_file(self, cr, uid, data, context={}):
        invoice_obj = self.pool.get('account.invoice')
        pac_params_obj = self.pool.get('params.pac')
        cfd_data = base64.decodestring( self.fdata )
        print 'dentro de upload ws es data es',data
        print 'el context es',context
        print 'el invoce_obj es',invoice_obj

        #~ invoice_ids = int(data['active_id'])
        #~ invoice_ids = context['active_id']
        invoice_ids = context.get('active_ids',[])
        print 'el invoice_ids es',invoice_ids
        invoice = invoice_obj.browse(cr, uid, invoice_ids, context=context)[0]
        print 'el invoice es', invoice
        #get currency and rate from invoice
        currency = invoice.currency_id.name
        currency_enc = currency.encode('UTF-8', 'strict')
        #currency_enc = ustr(currency)
        rate = invoice.currency_id.rate
        rate_str = str(rate)

        moneda = '''<Addenda>
            <sferp:Divisa codigoISO="%s" nombre="%s" tipoDeCambio="%s" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:sferp="http://www.solucionfactible.com/cfd/divisas" xsi:schemaLocation="http://www.solucionfactible.com/cfd/divisas http://solucionfactible.com/addenda/divisas.xsd"/>
        </Addenda> </Comprobante>'''%(currency_enc,currency_enc,rate_str)


        cfd_data_adenda = cfd_data.replace('</Comprobante>', moneda)
        pac_params_ids = pac_params_obj.search(cr,uid,[('method_type','=','pac_sf_firmar')], limit=1, context=context)

        if pac_params_ids:
            pac_params = pac_params_obj.browse(cr, uid, pac_params_ids, context)[0]
            user = pac_params.user
            password = pac_params.password
            wsdl_url = pac_params.url_webservice
            namespace = pac_params.namespace

            msg = 'no se pudo subir el archivo'
            if cfd_data_adenda:

                #~ wsdl_url = 'http://testing.solucionfactible.com/ws/services/TimbradoCFD?wsdl'  originales
                #~ namespace = 'http://timbradocfd.ws.cfdi.solucionfactible.com' originales
                #~ user = 'testing@solucionfactible.com' originales
                #~ password = 'timbrado.SF.16672' originales

                #try:
                #wsdl_client = WSDL.Proxy( wsdl_url, namespace )
                wsdl_client = WSDL.SOAPProxy( wsdl_url, namespace )
                #except:
                    #pass
                if True:#if wsdl_client:

                    file_globals = invoice_obj._get_file_globals(cr, uid, invoice_ids, context=context)
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
                    msg = resultado['resultados'] and resultado['resultados']['mensaje'] or ''
                    status = resultado['resultados'] and resultado['resultados']['status'] or ''
                    if status == '200' or status == '307':
                        fecha_timbrado = resultado['resultados']['fechaTimbrado'] or False
                        fecha_timbrado = fecha_timbrado and time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(fecha_timbrado[:19], '%Y-%m-%dT%H:%M:%S')) or False
                        cfdi_data = {
                            #'cfdi_cbb': base64.decodestring( resultado['resultados']['qrCode'] or '' ) or False,
                            'cfdi_cbb': resultado['resultados']['qrCode'] or False,#ya lo regresa en base64
                            'cfdi_sello': resultado['resultados']['selloSAT'] or False,
                            'cfdi_no_certificado': resultado['resultados']['certificadoSAT'] or False,
                            'cfdi_cadena_original': resultado['resultados']['cadenaOriginal'] or False,
                            'cfdi_fecha_timbrado': fecha_timbrado,
                            'cfdi_xml': base64.decodestring( resultado['resultados']['cfdiTimbrado'] or '' ),#este se necesita en uno que no es base64
                            'cfdi_folio_fiscal': resultado['resultados']['uuid'] or '' ,
                        }
                        invoice_obj.cfdi_data_write(cr, uid, [invoice.id], cfdi_data, context=context)
                        msg = msg + "\nAsegurese de que su archivo realmente haya sido generado correctamente ante el SAT\nhttps://www.consulta.sat.gob.mx/sicofi_web/moduloECFD_plus/ValidadorCFDI/Validador%20cfdi.html"

                        if cfdi_data['cfdi_xml']:
                            print 'el cfdi data es',cfdi_data['cfdi_xml']
                            escribe=self.write(cr, uid, data, {'message': msg, 'file':  base64.encodestring(cfdi_data['cfdi_xml']), }, context=None)
                        if not escribe:
                            print '--------------------no escribio en mensaje'
                        else:
                            print '------escribio'

                        #open("D:\\cfdi_b64.xml", "wb").write( resultado['resultados']['cfdiTimbrado'] or '' )
                        #open("D:\\cfdi.xml", "wb").write( base64.decodestring( resultado['resultados']['cfdiTimbrado'] or '' ) )
                    elif status == '500':#documento no es un cfd version 2, probablemente ya es un CFD version 3
                        msg = "Probablemente el archivo XML ya ha sido timbrado previamente y no es necesario volverlo a subir.\nO puede ser que el formato del archivo, no es el correcto.\nPor favor, visualice el archivo para corroborarlo y seguir con el siguiente paso o comuniquese con su administrador del sistema.\n" + ( resultado['resultados']['mensaje'] or '') + ( resultado['mensaje'] or '' )
                    else:
                        msg += '\n' + resultado['mensaje'] or ''
                        if not status:
                            status = 'parent_' + resultado['status']
        else:
            msg = 'No se encontro informacion del webservices del PAC, verifique que la configuración del PAC sea correcta'
        self.write(cr, uid, data, {'message': msg }, context=None)
        #~ return {'file': data['form']['file'], 'msg': msg}


        #~ print '-----------------------------antes del return de upload'
        #~ print 'el msg es',msg
        #~
        #~ if cfdi_data['cfdi_xml']:
            #~ print 'el cfdi data es',cfdi_data['cfdi_xml']
#~
#~
            #~ escribe=self.write(cr, uid, data, {'file': cfdi_data['cfdi_xml'],}, context=None)
            #~ if escribe:
                #~ print '--------------------si escribio'
            #~ else:
                #~ print '--------no escribio'
            #~ return cfdi_data['cfdi_xml']
            #~ raise osv.except_osv(('Estado de Timbrado!'),(msg))
        #~ else:
            #~ return False
            #~ raise osv.except_osv(('Estado de Timbrado!'),('nada de naa'))



    _columns = {
        'file': fields.binary('File', readonly=True),
        #~ 'file': fields.char('file',size=128),
        'message': fields.text('text'),

    }

    _defaults= {
        'message': 'Select upload button for export to PAC',
        'file': _get_file,
    }



#~
    #~ def upload_invoice(self, cr, uid, ids, context=None):
        #~ data = self.read(cr, uid, ids)[0]
        #~ print 'dentro de la funcion y data es',data
        #~ escribe=self.write(cr, uid, ids, {'message':'el mensaje de prueba',}, context=None)
        #~ print 'el escribe es:',escribe
#~
    #~ def sf_cancel(self, cr, uid, ids, context=None):
        #~ data = self.read(cr, uid, ids)[0]
        #~ context_id=context.get('active_ids',[])
#~
        #~ invoice_obj = self.pool.get('account.invoice')
        #~ company_obj = self.pool.get('res.company.facturae.certificate')
        #~ pac_params_obj = self.pool.get('params.pac')
#~
        #~ invoice_brw = invoice_obj.browse(cr, uid, context_id, context)[0]
        #~ company_brw = company_obj.browse(cr, uid, [invoice_brw.company_id.id], context)[0]
        #~ pac_params_srch = pac_params_obj.search(cr,uid,[('method_type','=','pac_sf_cancelar')],context=context)
#~
        #~ if pac_params_srch:
            #~ pac_params_brw = pac_params_obj.browse(cr, uid, pac_params_srch, context)[0]
#~
            #~ user = pac_params_brw.user
            #~ password = pac_params_brw.password
            #~ wsdl_url = pac_params_brw.url_webservice
            #~ namespace = pac_params_brw.namespace
            #~ #---------constantes
            #user = 'testing@solucionfactible.com'
            #password = 'timbrado.SF.16672'
            #wsdl_url = 'http://testing.solucionfactible.com/ws/services/Timbrado?wsdl'
            #namespace = 'http://timbrado.ws.cfdi.solucionfactible.com'
#~
            #~ cerCSD = company_brw.certificate_file#base64.encodestring(company_brw.certificate_file)
            #~ keyCSD = company_brw.certificate_key_file#base64.encodestring(company_brw.certificate_key_file)
            #~ contrasenaCSD = company_brw.certificate_password
            #~ uuids = invoice_brw.cfdi_folio_fiscal#cfdi_folio_fiscal
#~
            #~ wsdl_client = False        })

            #~ wsdl_client = WSDL.SOAPProxy( wsdl_url, namespace )
            #~ if True:#if wsdl_client:
                #~ params = [user, password, uuids, cerCSD, keyCSD, contrasenaCSD ]
                #~ wsdl_client.soapproxy.config.dumpSOAPOut = 0
                #~ wsdl_client.soapproxy.config.dumpSOAPIn = 0
                #~ wsdl_client.soapproxy.config.debug = 0
                #~ wsdl_client.soapproxy.config.dict_encoding='UTF-8'
                #~ resultado = wsdl_client.cancelar(*params)
#~
                #~ status = resultado['resultados']['status']
                #~ status_uuid = resultado['resultados']['statusUUID']
                #~ msg_status={}
                #~ if status =='200':
                    #~ mensaje_global = '- El proceso de cancelación se ha completado correctamente'
                #~ elif status =='500':
                    #~ mensaje_global = '- Han ocurrido errores que no han permitido completar el proceso de cancelación'
                #~ folio_cancel = resultado['resultados']['uuid']
                #~ mensaje_global = mensaje_global +'\n- El uuid cancelado es: ' + folio_cancel
#~
                #~ if status_uuid == '201':
                    #~ mensaje_SAT = '\n- Estatus de respuesta del SAT: 201. El folio se ha cancelado con éxito'
                #~ elif status_uuid == '202':
                    #~ mensaje_SAT = '\n- Estatus de respuesta del SAT: 202. El folio ya se había cancelado previamente'
                #~ elif status_uuid == '203':
                    #~ mensaje_SAT = '\n- Estatus de respuesta del SAT: 203. El comprobante que intenta cancelar no corresponde al contribuyente con el que se ha firmado la solicitud de cancelación'
                #~ elif status_uuid == '204':
                    #~ mensaje_SAT = '\n- Estatus de respuesta del SAT: 204. El CFDI no aplica para cancelación'
                #~ elif status_uuid == '205':
                    #~ mensaje_SAT = '\n- Estatus de respuesta del SAT: 205. No se encuentra el folio del CFDI para su cancelación'
                #~ else:
                    #~ mensaje_SAT = '- Etatus uuid desconocido'
                #~ mensaje_global = mensaje_global + mensaje_SAT
#~
                #~ print 'mensaje final es: ',mensaje_global.decode(encoding='UTF-8', errors='strict')
                #~ raise osv.except_osv(('Estado de Cancelacion!'),(mensaje_global.decode(encoding='UTF-8', errors='strict')))
        #~ else:
            #~ mensaje_global='No se encontro información del webservices del PAC, verifique que la configuración del PAC sea correcta'
            #~ raise osv.except_osv(('Estado de Cancelacion!'),(mensaje_global.decode(encoding='UTF-8', errors='strict')))
        #~ return {}

wizard_export_invoice_pac_sf_v6()

