# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Luis Torres (luis_t260@vauxoo.com)
#    Financed by: http://www.sfsoluciones.com (aef@sfsoluciones.com)
#
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
#
from openerp.osv import osv, fields
import tempfile
import os
import codecs
import base64
import xml.dom.minidom
from datetime import datetime, timedelta
from openerp.tools.translate import _
try:
    from SOAPpy import WSDL
except:
    print "Package SOAPpy missed"
    pass
import time


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def _get_facturae_invoice_dict_data(self, cr, uid, ids, context={}):
        datas = super(account_invoice, self)._get_facturae_invoice_dict_data(
            cr, uid, ids, context=context)
        ir_seq_app_obj = self.pool.get('ir.sequence.approval')
        invoice = self.browse(cr, uid, ids[0], context=context)
        sequence_app_id = ir_seq_app_obj.search(cr, uid, [(
            'sequence_id', '=', invoice.invoice_sequence_id.id)], context=context)
        type_inv = 'cfd22'
        if sequence_app_id:
            type_inv = ir_seq_app_obj.browse(
                cr, uid, sequence_app_id[0], context=context).type
        for data in datas:
            if 'cfdi' in type_inv:
                comprobante = data['Comprobante']
                rfc = comprobante['Emisor']['rfc']
                nombre = comprobante['Emisor']['nombre']
                dom_Fiscal = comprobante['Emisor']['DomicilioFiscal']
                exp_en = comprobante['Emisor']['ExpedidoEn']
                reg_Fiscal = comprobante['Emisor']['RegimenFiscal']
                rfc_receptor = comprobante['Receptor']['rfc']
                nombre_receptor = comprobante['Receptor']['nombre']
                domicilio_receptor = comprobante['Receptor']['Domicilio']
                totalImpuestosTrasladados = comprobante[
                    'Impuestos']['totalImpuestosTrasladados']
                dict_cfdi_comprobante = {}
                dict_emisor = dict({'rfc': rfc, 'nombre': nombre,
                                    'cfdi:DomicilioFiscal': dom_Fiscal, 'cfdi:ExpedidoEn':
                                    exp_en, 'cfdi:RegimenFiscal': reg_Fiscal})
                dict_receptor = dict({'rfc': rfc_receptor,
                                      'nombre': nombre_receptor, 'cfdi:Domicilio': domicilio_receptor})
                list_conceptos = []
                dict_impuestos = dict({'totalImpuestosTrasladados':
                                       totalImpuestosTrasladados, 'cfdi:Traslados': []})
                for concepto in comprobante['Conceptos']:
                    list_conceptos.append(dict({'cfdi:Concepto':
                                                concepto['Concepto']}))
                for traslado in comprobante['Impuestos']['Traslados']:
                    dict_impuestos['cfdi:Traslados'].append(dict(
                        {'cfdi:Traslado': traslado['Traslado']}))
                comprobante.update({'cfdi:Emisor': dict_emisor,
                                    'cfdi:Receptor': dict_receptor,
                                    'cfdi:Conceptos': list_conceptos,
                                    'cfdi:Impuestos': dict_impuestos,
                                    })
                comprobante.pop('Emisor')
                comprobante.pop('Impuestos')
                comprobante.pop('Conceptos')
                comprobante.pop('Receptor')
                comprobante.pop('xsi:schemaLocation')
                comprobante.update(
                    {'xmlns:cfdi': "http://www.sat.gob.mx/cfd/3",
                     'xsi:schemaLocation': "http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv32.xsd",
                     'version': "3.2", })
                comprobante.pop('xmlns')
                dict_comprobante = comprobante
                data.pop('Comprobante')
                data.update(dict({'cfdi:Comprobante': dict_comprobante}))
        return datas

    def _get_facturae_invoice_xml_data(self, cr, uid, ids, context={}):
        if not context:
            context = {}
        ir_seq_app_obj = self.pool.get('ir.sequence.approval')
        invoice = self.browse(cr, uid, ids[0], context=context)
        sequence_app_id = ir_seq_app_obj.search(cr, uid, [(
            'sequence_id', '=', invoice.invoice_sequence_id.id)], context=context)
        type_inv = 'cfd22'
        if sequence_app_id:
            type_inv = ir_seq_app_obj.browse(
                cr, uid, sequence_app_id[0], context=context).type
        if 'cfdi' in type_inv:
            comprobante = 'cfdi:Comprobante'
            emisor = 'cfdi:Emisor'
            receptor = 'cfdi:Receptor'
            concepto = 'cfdi:Conceptos'
        else:
            comprobante = 'Comprobante'
            emisor = 'Emisor'
            regimenFiscal = 'RegimenFiscal'
            receptor = 'Receptor'
            concepto = 'Conceptos'

        data_dict = self._get_facturae_invoice_dict_data(
            cr, uid, ids, context=context)[0]
        doc_xml = self.dict2xml({comprobante: data_dict.get(comprobante)})
        invoice_number = "sn"
        (fileno_xml, fname_xml) = tempfile.mkstemp(
            '.xml', 'openerp_' + (invoice_number or '') + '__facturae__')
        fname_txt = fname_xml + '.txt'
        f = open(fname_xml, 'w')
        doc_xml.writexml(
            f, indent='    ', addindent='    ', newl='\r\n', encoding='UTF-8')
        f.close()
        os.close(fileno_xml)

        (fileno_sign, fname_sign) = tempfile.mkstemp('.txt', 'openerp_' + (
            invoice_number or '') + '__facturae_txt_md5__')
        os.close(fileno_sign)
        
        context.update({
            'fname_xml': fname_xml,
            'fname_txt': fname_txt,
            'fname_sign': fname_sign,
        })
        context.update(self._get_file_globals(cr, uid, ids, context=context))
        fname_txt, txt_str = self._xml2cad_orig(
            cr=False, uid=False, ids=False, context=context)
        data_dict['cadena_original'] = txt_str
        msg2=''

        if not txt_str:
            raise osv.except_osv(_('Error in Original String!'), _(
                "Can't get the string original of the voucher.\nCkeck your configuration.\n%s" % (msg2)))

        if not data_dict[comprobante].get('folio', ''):
            raise osv.except_osv(_('Error in Folio!'), _(
                "Can't get the folio of the voucher.\nBefore generating the XML, click on the button, generate invoice.\nCkeck your configuration.\n%s" % (msg2)))

        context.update({'fecha': data_dict[comprobante]['fecha']})
        sign_str = self._get_sello(
            cr=False, uid=False, ids=False, context=context)
        if not sign_str:
            raise osv.except_osv(_('Error in Stamp !'), _(
                "Can't generate the stamp of the voucher.\nCkeck your configuration.\ns%s") % (msg2))

        nodeComprobante = doc_xml.getElementsByTagName(comprobante)[0]
        nodeComprobante.setAttribute("sello", sign_str)
        data_dict[comprobante]['sello'] = sign_str

        noCertificado = self._get_noCertificado(context['fname_cer'])
        if not noCertificado:
            raise osv.except_osv(_('Error in No. Certificate !'), _(
                "Can't get the Certificate Number of the voucher.\nCkeck your configuration.\n%s") % (msg2))
        nodeComprobante.setAttribute("noCertificado", noCertificado)
        data_dict[comprobante]['noCertificado'] = noCertificado

        cert_str = self._get_certificate_str(context['fname_cer'])
        if not cert_str:
            raise osv.except_osv(_('Error in Certificate!'), _(
                "Can't get the Certificate Number of the voucher.\nCkeck your configuration.\n%s") % (msg2))
        cert_str = cert_str.replace(' ', '').replace('\n', '')
        nodeComprobante.setAttribute("certificado", cert_str)
        data_dict[comprobante]['certificado'] = cert_str

        nodeComprobante.removeAttribute('anoAprobacion')
        nodeComprobante.removeAttribute('noAprobacion')

        x = doc_xml.documentElement
        nodeReceptor = doc_xml.getElementsByTagName(receptor)[0]
        nodeConcepto = doc_xml.getElementsByTagName(concepto)[0]
        x.insertBefore(nodeReceptor, nodeConcepto)

        self.write_cfd_data(cr, uid, ids, data_dict, context=context)

        if context.get('type_data') == 'dict':
            return data_dict
        if context.get('type_data') == 'xml_obj':
            return doc_xml
        data_xml = doc_xml.toxml('UTF-8')
        data_xml = codecs.BOM_UTF8 + data_xml
        fname_xml = (data_dict[comprobante][emisor]['rfc'] or '') + '_' + (
            data_dict[comprobante].get('serie', '') or '') + '_' + (
            data_dict[comprobante].get('folio', '') or '') + '.xml'
        data_xml = data_xml.replace(
            '<?xml version="1.0" encoding="UTF-8"?>', '<?xml version="1.0" encoding="UTF-8"?>\n')
        return fname_xml, data_xml
