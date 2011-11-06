# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://moylop.blogspot.com/
#    All Rights Reserved.
#    info moylop260 (moylop260@hotmail.com)
############################################################################
#    Coded by: moylop260 (moylop260@hotmail.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@openerp.com.ve
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


from osv import osv
from osv import fields
import netsvc
import base64
import time
import codecs
try:
    from SOAPpy import WSDL
except:
    print "Package SOAPpy missed"
    pass

class ir_attachment_facturae_mx(osv.osv):
    _inherit = 'ir.attachment.facturae.mx'

    def _get_type(self, cr, uid, ids=None, context=None):
        types = super(ir_attachment_facturae_mx, self)._get_type(cr, uid, ids, context=context)
        types.append( ('cfdi2011_pac_solfact', 'CFDI 2011 PAC Solucion Factible') )
        return types
    
    _columns = {
        'type': fields.selection(_get_type, 'Type', type='char', size=64),
    }
    
    #def action_confirm(self, cr, uid, ids, context=None):
        #return self.write(cr, uid, ids, {'state': 'confirmed'})
    def sign_pac_solfact(self, cr, uid, ids, context=None):
        print "entro a sign_pac_solfact"
        invoice_obj = self.pool.get('account.invoice')
        pac_params_obj = self.pool.get('params.pac')
        #TODO: Agregar moneda, al crear (transformar info)
        #cfd_data = base64.decodestring( data['form']['file'] or '' )
        #invoice_ids = data['ids']
        #invoice = invoice_obj.browse(cr, uid, invoice_ids, context=context)[0]
        #get currency and rate from invoice
        
        pac_params_ids = pac_params_obj.search(cr,uid,[('method_type','=','pac_sf_firmar')], limit=1, context=context)
        if pac_params_ids:
            pac_params = pac_params_obj.browse(cr, uid, pac_params_ids, context)[0]
            user = pac_params.user
            password = pac_params.password
            wsdl_url = pac_params.url_webservice
            namespace = pac_params.namespace

            msg = 'no se pudo subir el archivo'
            #if cfd_data_adenda:
            if True:

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
                    for attachment in self.browse(cr, uid, ids, context=context):
                        invoice = attachment.invoice_id
                        file_globals = invoice_obj._get_file_globals(cr, uid, [attachment.invoice_id.id], context=context)
                        currency = invoice.currency_id.name
                        currency_enc = currency.encode('UTF-8', 'strict')
                        ##currency_enc = ustr(currency)
                        #TODO: Mandar en el context, la fecha para calcular la moneda, o extraer el rate de otro lado.
                        rate = invoice.currency_id.rate
                        rate_str = str(rate)
                        moneda = '''<Addenda>
                            #<sferp:Divisa codigoISO="%s" nombre="%s" tipoDeCambio="%s" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:sferp="http://www.solucionfactible.com/cfd/divisas" xsi:schemaLocation="http://www.solucionfactible.com/cfd/divisas http://solucionfactible.com/addenda/divisas.xsd"/>
                        #</Addenda> </Comprobante>'''%(currency_enc,currency_enc,rate_str)
                        cfd_data = base64.decodestring( attachment.file_input or '')
                        cfd_data_adenda = cfd_data.replace('</Comprobante>', moneda)
                        cfd_data = cfd_data_adenda
                        
                        fname_cer_no_pem = file_globals['fname_cer']
                        cerCSD = fname_cer_no_pem and base64.encodestring( open(fname_cer_no_pem, "r" ).read() ) or ''
                        fname_key_no_pem = file_globals['fname_key']
                        keyCSD = fname_key_no_pem and base64.encodestring( open(fname_key_no_pem, "r" ).read() ) or ''
                        
                        #cfdi = base64.encodestring( cfd_data_adenda.replace(codecs.BOM_UTF8,'') )
                        cfdi = base64.encodestring( cfd_data_adenda )
                        #cfdi = cfd_data
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
                            invoice_obj.cfdi_data_write(cr, uid, [invoice.id], cfdi_data, context=context)#TODO: pasar toda esta informacion al modelo de attachment facturaefs
                            
                            attachment_data = {
                                #'file_xml_sign': base64.decodestring( resultado['resultados']['cfdiTimbrado'] or '' ),#este se necesita en uno que no es base64
                                'file_xml_sign': resultado['resultados']['cfdiTimbrado'] or False
                            }
                            self.write(cr, uid, [attachment.id], attachment_data, context=context)
                            
                            msg = msg + "\nAsegurese de que su archivo realmente haya sido generado correctamente ante el SAT\nhttps://www.consulta.sat.gob.mx/sicofi_web/moduloECFD_plus/ValidadorCFDI/Validador%20cfdi.html"
                            #print "resultado['resultados']['uuid']",resultado['resultados']['uuid']
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
        #TODO: Guardar el mensaje de la operacion
        print "msg",msg
        return True
        
    def action_sign(self, cr, uid, ids, context=None):
        for attachment in self.browse(cr, uid, ids, context=context):
            if attachment.type == 'cfdi2011_pac_solfact':
                self.sign_pac_solfact(cr, uid, [attachment.id], context=context)
        res = super(ir_attachment_facturae_mx, self).action_sign(cr, uid, ids, context=context)
        return res
    
    def action_printable(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'printable'})

    def action_send_email(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'sent_email'})
    
    def action_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'})
    
    def action_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'})
    
ir_attachment_facturae_mx()
