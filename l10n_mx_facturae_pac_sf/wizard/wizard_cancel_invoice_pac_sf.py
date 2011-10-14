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


class wizard_cancel_invoice_pac_sf(osv.osv_memory):
    _name='wizard.cancel.invoice.pac.sf'


    def sf_cancel(self, cr, uid, ids, context=None):
        print 'esta dentro del cancel'
        user = 'testing@solucionfactible.com'
        password = 'timbrado.SF.16672'

        context_id=context.get('active_ids',[])
        print context_id
        print 'context= ',context

        invoice_obj = self.pool.get('account.invoice')
        company_obj = self.pool.get('res.company.facturae.certificate')
        invoice_brw = invoice_obj.browse(cr, uid, context_id, context)[0]
        company_brw = company_obj.browse(cr, uid, [invoice_brw.company_id.id], context)[0]
        print 'el invoice_brw',invoice_brw

        #~ params=[user, password, cfdi, cerCSD, keyCSD, contrasenaCSD, zip]
        print 'company_id es: ',invoice_brw.company_id.id

        cerCSD = company_brw.certificate_file#base64.encodestring(company_brw.certificate_file)
        keyCSD = company_brw.certificate_key_file#base64.encodestring(company_brw.certificate_key_file)
        contrasenaCSD = company_brw.certificate_password
        uuids = invoice_brw.cfdi_folio_fiscal#cfdi_folio_fiscal
#~
        #~ print 'el certificate file es: ',cerCSD
        #~ print 'el certificate key file es: ',keyCSD
        #~ print 'el certificate password es: ',contrasenaCSD
        #~ print 'el uuids folio fiscal es: ',uuids


        print '----------------------------inicia envio a pac-------------------------------'

        #~ wsdl_url = 'http://testing.solucionfactible.com/ws/services/TimbradoCFD?wsdl' #moy
        #~ namespace = 'http://timbradocfd.ws.cfdi.solucionfactible.com'#moy

        wsdl_url = 'http://testing.solucionfactible.com/ws/services/Timbrado?wsdl'#url buenas
        namespace = 'http://timbrado.ws.cfdi.solucionfactible.com'#url Buenas

        wsdl_client = False
        #try:
        #wsdl_client = WSDL.Proxy( wsdl_url, namespace )
        wsdl_client = WSDL.SOAPProxy( wsdl_url, namespace )
        #except:
            #pass
        if True:#if wsdl_client:
            params = [user, password, uuids, cerCSD, keyCSD, contrasenaCSD ]
            print '-----------------inicia llamado al web service'
            wsdl_client.soapproxy.config.dumpSOAPOut = 0
            wsdl_client.soapproxy.config.dumpSOAPIn = 0
            wsdl_client.soapproxy.config.debug = 0
            wsdl_client.soapproxy.config.dict_encoding='UTF-8'
            #~ print 'antes de obtener resultado params es: ',params
            resultado = wsdl_client.cancelar(*params)

            #~ msg = resultado['resultados']['mensaje']
            #~ status = resultado['resultados']['status']
            #~ print "--------------El resultado es: ",resultado

            status = resultado['resultados']['status']
            status_uuid = resultado['resultados']['statusUUID']
            if status =='200':
                print 'El proceso de cancelación se ha completado correctamente, estatus ',status
            elif status =='500':
                print 'Han ocurrido errores que no han permitido completar el proceso de cancelación ',status

            print 'El mensaje del resultado es: ',resultado['resultados']['mensaje']
            print 'El uuid cancelado es: ',resultado['resultados']['uuid']
            if status_uuid == '201':
                print 'El folio se ha cancelado con éxito, status_uuid: ',status_uuid
            elif status_uuid == '202':
                print 'El folio ya se había cancelado previamente, status_uuid: ',status_uuid
            elif status_uuid == '203':
                print 'El comprobante que intenta cancelar no corresponde al contribuyente con el que se ha firmado la solicitud de cancelación, status_uuid: ',status_uuid
            elif status_uuid == '204':
                print 'El CFDI no aplica para cancelación, status_uuid: ',status_uuid
            elif status_uuid == '205':
                print 'No se encuentra el folio del CFDI para su cancelación, status_uuid: ',status_uuid
            else:
                print 'status uuid desconocido',status_uuid

        return {}

wizard_cancel_invoice_pac_sf()

