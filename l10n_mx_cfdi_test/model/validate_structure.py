# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: vauxoo consultores (info@vauxoo.com)
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
from openerp.osv import fields, osv
import base64
import xml

class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def validate_amounts(self, cr, uid, ids, xml_binary, invoice_id, context=None):
        if context is None:
            context = {}
        ir_model_data = self.pool.get('ir.model.data')
        aml_obj = self.pool.get('account.invoice.line')
        tax_obj = self.pool.get('account.invoice.tax')
        data_xml = base64.decodestring( xml_binary )
        doc_xml = xml.dom.minidom.parseString(data_xml)
        tax_lines = self.read(cr, uid, [ids],['tax_line'])
        invoice_lines = self.read(cr, uid, [ids],['invoice_line'])
        data_invoice = self.read(cr, uid, ids,[])
        list_price_subtotal = []
        list_price_unit = []
        list_importe_xml = []
        list_valorUnitario_xml = []
        list_retenciones = []
        list_traslados = []
        list_importe_ret_xml = []
        list_importe_traslados_xml = []
        totalImpuestosRetenidos = 0.00
        totalImpuestosTrasladados = 0.00
        totalImpuestosRetenidos_xml = 0.00
        totalImpuestosTrasladados_xml = 0.00
        amount_total_tax = 0.00
        importe_ret = 0.00
        if invoice_lines:
            for n in doc_xml.getElementsByTagName("cfdi:Comprobante"):
                xml_total = n.getAttribute("total")
                xml_subTotal = n.getAttribute("subTotal")
                assert data_invoice['amount_total'] == eval(xml_total), 'No matches Total'
                assert data_invoice['amount_untaxed'] == eval(xml_subTotal), 'No matches Subtotal'
            for line in invoice_lines[0]['invoice_line']:
                for r in aml_obj.read(cr, uid, [line]):
                    list_price_subtotal.append(r['price_subtotal'])
                    list_price_unit.append(r['price_unit'])
            for n in doc_xml.getElementsByTagName("cfdi:Comprobante"):
                for conceptos in n.getElementsByTagName("cfdi:Conceptos"):
                    for concepto in conceptos.getElementsByTagName("cfdi:Concepto"):
                        importe = concepto.getAttribute("importe")
                        valorUnitario =  concepto.getAttribute("valorUnitario")
                        list_importe_xml.append(eval(importe))
                        list_valorUnitario_xml.append(eval(valorUnitario))
            assert list_price_subtotal == list_importe_xml, 'No matches Importe of product'
            assert list_price_unit == list_valorUnitario_xml, 'No matches Price Unit of product'
            for tax in tax_lines[0]['tax_line']:
                for t in tax_obj.read(cr, uid, [tax]):
                    if t['amount'] >= 0:
                        traslado = abs(t['amount']) or 0.0
                        list_traslados.append(traslado)
                        totalImpuestosTrasladados += traslado or 0.0
                    else:
                        retencion = abs(t['amount']) or 0.0
                        list_retenciones.append(retencion)
                        totalImpuestosRetenidos += retencion or 0.0
            for taxes in n.getElementsByTagName("cfdi:Impuestos"):
                totalImpuestosTrasladados_xml = eval(taxes.getAttribute("totalImpuestosTrasladados"))
                totalImpuestosRetenidos_xml = eval(taxes.getAttribute("totalImpuestosRetenidos"))
                if taxes.getElementsByTagName("cfdi:Retenciones"):
                    for retenciones in taxes.getElementsByTagName("cfdi:Retenciones"):
                        for ret in retenciones.getElementsByTagName("cfdi:Retencion"):
                            list_importe_ret_xml.append(eval(ret.getAttribute("importe")))
                if taxes.getElementsByTagName("cfdi:Traslados"):
                    for traslados in taxes.getElementsByTagName("cfdi:Traslados"):
                        for traslado in traslados.getElementsByTagName("cfdi:Traslado"):
                            list_importe_traslados_xml.append(eval(traslado.getAttribute("importe")))
            assert totalImpuestosRetenidos == totalImpuestosRetenidos_xml, 'No matches Total Impuestos Retenidos of product'
            assert totalImpuestosTrasladados == totalImpuestosTrasladados_xml, 'No matches Total Impuestos Trasladados of product'
            assert list_retenciones == list_importe_ret_xml, 'No matches Importe Retenido of product'
            assert list_traslados == list_importe_traslados_xml, 'No matches Importe Traslado of product'
        return True
