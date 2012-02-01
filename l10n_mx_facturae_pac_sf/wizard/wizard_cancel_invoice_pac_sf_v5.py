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

_form = '''<?xml version="1.0"?>
<form string="Cancel CFDI PAC SF">
    <separator colspan="4" string="File"/>
        <field name='file' nolabel="1" colspan="4"/>
        <newline/>
        <separator colspan="4" string="Message"/>
        <field name='message' nolabel="1" colspan="4"/>
    <separator string="" colspan="4"/>
</form>'''

_fields = {
   'file': {
        'string': 'Name',
        'type': 'binary',
    },
   'message': {
        'string': 'Message',
        'type': 'text',
   },
}

def sf_cancel(self, cr, uid, data, context=None):
        pool = pooler.get_pool(cr.dbname)
        #data = self.read(cr, uid, ids)[0]
        context_id=context.get('active_ids',[])

        invoice_obj = pool.get('account.invoice')
        company_obj = pool.get('res.company.facturae.certificate')
        pac_params_obj = pool.get('params.pac')

        invoice_brw = invoice_obj.browse(cr, uid, context_id, context)[0]
        company_brw = company_obj.browse(cr, uid, [invoice_brw.company_id.id], context)[0]
        pac_params_srch = pac_params_obj.search(cr,uid,[('method_type','=','pac_sf_cancelar')],context=context)

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
            
            #print "company_brw",company_brw
            #print "company_brw.certificate_file",company_brw.certificate_file
            """
            context.update( {'date_work': invoice_brw.date_invoice} )
            certificate_id = pool.get('res.company')._get_current_certificate(cr, uid, [invoice_brw.company_id.id], context=context)[invoice_brw.company_id.id]
            certificate = certificate_id and pool.get('res.company.facturae.certificate').browse(cr, uid, [certificate_id], context=context)[0] or False
            
            cerCSD = certificate.certificate_file 
            
            #cerCSD = company_brw.certificate_file#base64.encodestring(company_brw.certificate_file)
            keyCSD = certificate.certificate_key_file#base64.encodestring(company_brw.certificate_key_file)
            contrasenaCSD = certificate.certificate_password
            """
            
            wsdl_client = False
            wsdl_client = WSDL.SOAPProxy( wsdl_url, namespace )
            if True:#if wsdl_client:
                file_globals = invoice_obj._get_file_globals(cr, uid, context_id, context=context)
                fname_cer_no_pem = file_globals['fname_cer']
                cerCSD = fname_cer_no_pem and base64.encodestring( open(fname_cer_no_pem, "r" ).read() ) or ''
                fname_key_no_pem = file_globals['fname_key']
                keyCSD = fname_key_no_pem and base64.encodestring( open(fname_key_no_pem, "r" ).read() ) or ''
                #cfdi = base64.encodestring( cfd_data_adenda.replace(codecs.BOM_UTF8,'') )
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
        #self.write(cr, uid, ids, {'message': msg_global }, context=None)
        return {'message': msg_global }

def _get_file(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        atta_obj = pool.get('ir.attachment')
        atta_id = atta_obj.search(cr, uid, [('res_id', '=', context['active_id']), ('name', 'ilike', '%.xml')], context=context)
        res={}
        if atta_id:
            atta_brw = atta_obj.browse(cr, uid, atta_id, context)[0]
            inv_xml = atta_brw.datas or False

        else:
            inv_xml = False
            raise osv.except_osv(('Estado de Cancelación!'),('Esta factura no ha sido timbrada, por lo que no es posible cancelarse.'))
        return {'file': inv_xml}

class wizard_cancel_invoice_pac_sf_v5(wizard.interface):
    states = {
        'init': {
            'actions': [ _get_file ],
            'result': {'type': 'state', 'state':'show_view'},
        },

        'show_view': {
            'actions': [ ],
            'result': {
                'type': 'form',
                'arch': _form,
                'fields': _fields,
                'state': [ ('end', '_Cerrar', 'gtk-cancel', False), ('sf_cancel', '_Cancelar CFDI', 'gtk-ok', True) ]
            }
        },

        'sf_cancel': {
            'actions': [ sf_cancel ],
            'result': {'type': 'state', 'state':'show_view'},
        },
    }
wizard_cancel_invoice_pac_sf_v5('wizard.cancel.invoice.pac.sf.v5')
