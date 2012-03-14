# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
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
        data = self.read(cr, uid, ids)[0]
        context_id=context.get('active_ids',[])
        invoice_obj = self.pool.get('account.invoice')
        company_obj = self.pool.get('res.company.facturae.certificate')
        pac_params_obj = self.pool.get('params.pac')

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

            cerCSD = company_brw.certificate_file#base64.encodestring(company_brw.certificate_file)
            keyCSD = company_brw.certificate_key_file#base64.encodestring(company_brw.certificate_key_file)
            passcsd = company_brw.certificate_password
            uuids = invoice_brw.cfdi_folio_fiscal#cfdi_folio_fiscal

            wsdl_client = False
            wsdl_client = WSDL.SOAPProxy( wsdl_url, namespace )
            if True:#if wsdl_client:
                params = [user, password, uuids, cerCSD, keyCSD, passcsd ]
                wsdl_client.soapproxy.config.dumpSOAPOut = 0
                wsdl_client.soapproxy.config.dumpSOAPIn = 0
                wsdl_client.soapproxy.config.debug = 0
                wsdl_client.soapproxy.config.dict_encoding='UTF-8'
                result = wsdl_client.cancelar(*params)
                status = result['resultados'] and result['resultados']['status'] or ''
                status_uuid = result['resultados'] and result['resultados']['statusUUID'] or ''
                msg_status={}
                if status =='200':
                    folio_cancel = result['resultados'] and result['resultados']['uuid'] or ''
                    msg_global = '- El proceso de cancelación se ha completado correctamente.\n- El uuid cancelado es: ' + folio_cancel
                    #~ msg_global = msg_global +'\n- El uuid cancelado es: ' + folio_cancel
                #~ elif status =='500':
                    #~ msg_global = '- Han ocurrido errores que no han permitido completar el proceso de cancelación'
                else:
                    msg_global = '- Han ocurrido errores que no han permitido completar el proceso de cancelación, asegurese de que la factura que intenta cancelar ha sido timbrada previamente'

                if status_uuid == '201':
                    msg_sat = '\n- Estatus de respuesta del SAT: 201. El folio se ha cancelado con éxito.'
                    invoice_obj.write(cr, uid, context_id, {'cfdi_fecha_cancelacion':time.strftime('%d-%m-%Y %H:%M:%S')})
                elif status_uuid == '202':
                    msg_sat = '\n- Estatus de respuesta del SAT: 202. El folio ya se había cancelado previamente'
                elif status_uuid == '203':
                    msg_sat = '\n- Estatus de respuesta del SAT: 203. El comprobante que intenta cancelar no corresponde al contribuyente con el que se ha firmado la solicitud de cancelación'
                elif status_uuid == '204':
                    msg_sat = '\n- Estatus de respuesta del SAT: 204. El CFDI no aplica para cancelación'
                elif status_uuid == '205':
                    msg_sat = '\n- Estatus de respuesta del SAT: 205. No se encuentra el folio del CFDI para su cancelación'
                else:
                    msg_sat = '\n- Estatus de respuesta del SAT desconocido'
                msg_global = msg_global + msg_sat

        else:
            msg_global='No se encontro información del webservices del PAC, verifique que la configuración del PAC sea correcta'
        self.write(cr, uid, ids, {'message': msg_global }, context=None)
        return True

    def _get_file(self,cr, uid, context):
        atta_obj = self.pool.get('ir.attachment')
        atta_id = atta_obj.search(cr, uid, [('res_id', '=', context['active_id']), ('name', 'ilike', '%.xml')], context=context)
        res={}
        if atta_id:
            atta_brw = atta_obj.browse(cr, uid, atta_id, context)[0]
            inv_xml = base64.encodestring(atta_brw.db_datas)

        else:
            inv_xml = False
            raise osv.except_osv(('Estado de Cancelación!'),('Esta factura no ha sido timbrada, por lo que no es posible cancelarse.'))
        return inv_xml


    _columns = {
        'file': fields.binary('File', readonly=True),
        'message': fields.text('text'),

    }

    _defaults= {
        'message': 'Seleccione el botón Cancelar Factura para exportar al PAC',
        'file': _get_file
    }
wizard_cancel_invoice_pac_sf()

