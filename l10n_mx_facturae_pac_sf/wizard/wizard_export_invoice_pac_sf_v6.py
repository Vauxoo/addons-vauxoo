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
import xml.dom.minidom
from datetime import datetime
from tools.misc import ustr
try:
    from SOAPpy import WSDL
except:
    print "Package SOAPpy missed"
    pass
import time


class wizard_export_invoice_pac_sf_v6(osv.osv_memory):
    _name='wizard.export.invoice.pac.sf.v6'

    def _get_file(self, cr, uid, data, context={}):
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
        self.fdata=fdata
        self.msg=msg
        self.fdata=fdata
        self.id=id
        return fdata
        #~ return {'file': fdata, 'fname': fname_invoice, 'msg': msg}

    def upload_ws_file(self, cr, uid, data, context={}):
        invoice_obj = self.pool.get('account.invoice')
        pac_params_obj = self.pool.get('params.pac')
        #TODO: Change get file of xml from model browse of wizard
        cfd_data = base64.decodestring( self.fdata )

        xml_res_str = xml.dom.minidom.parseString(cfd_data)
        compr = xml_res_str.getElementsByTagName('Comprobante')[0]
        date = compr.attributes['fecha'].value
        date_format = datetime.strptime( date, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
        context['date']=date_format

        invoice_ids = context.get('active_ids',[])
        invoice = invoice_obj.browse(cr, uid, invoice_ids, context=context)[0]

        currency = invoice.currency_id.name
        currency_enc = currency.encode('UTF-8', 'strict')

        rate = invoice.currency_id.rate and (1.0/invoice.currency_id.rate) or 1

        moneda = '''<Addenda>
            <sferp:Divisa codigoISO="%s" nombre="%s" tipoDeCambio="%s" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:sferp="http://www.solucionfactible.com/cfd/divisas" xsi:schemaLocation="http://www.solucionfactible.com/cfd/divisas http://solucionfactible.com/addenda/divisas.xsd"/>
        </Addenda> </Comprobante>'''%(currency_enc,currency_enc,rate)

        cfd_data_adenda = cfd_data.replace('</Comprobante>', moneda)
        pac_params_ids = pac_params_obj.search(cr,uid,[('method_type','=','pac_sf_firmar')], limit=1, context=context)

        if pac_params_ids:
            pac_params = pac_params_obj.browse(cr, uid, pac_params_ids, context)[0]
            user = pac_params.user
            password = pac_params.password
            wsdl_url = pac_params.url_webservice
            namespace = pac_params.namespace

            msg = 'No se pudo subir el archivo'
            if cfd_data_adenda:

                #~ wsdl_url = 'http://testing.solucionfactible.com/ws/services/TimbradoCFD?wsdl'  originales
                #~ namespace = 'http://timbradocfd.ws.cfdi.solucionfactible.com' originales
                #~ user = 'testing@solucionfactible.com' originales
                #~ password = 'timbrado.SF.16672' originales

                wsdl_client = WSDL.SOAPProxy( wsdl_url, namespace )

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
                    if status == '200':
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
                        if cfdi_data.get('cfdi_xml', False):
                            file = cfdi_data.get('cfdi_xml', False)
                            invoice_obj.cfdi_data_write(cr, uid, [invoice.id], cfdi_data, context=context)
                            msg = msg + "\nAsegurese de que su archivo realmente haya sido generado correctamente ante el SAT\nhttps://www.consulta.sat.gob.mx/sicofi_web/moduloECFD_plus/ValidadorCFDI/Validador%20cfdi.html"
                            self.write(cr, uid, data, {'message': msg, 'file':  base64.encodestring(file) }, context=None)#TODO: Write ever to final of function
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
        self.write(cr, uid, data, {'message': msg }, context=None)
        return True
    
    _columns = {
        'file': fields.binary('File', readonly=True),
        'message': fields.text('text'),
    }

    _defaults= {
        'message': 'Seleccione el botón Subir Factura para exportar al PAC',
        'file': _get_file,
    }

wizard_export_invoice_pac_sf_v6()

