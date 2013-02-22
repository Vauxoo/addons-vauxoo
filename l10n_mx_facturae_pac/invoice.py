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
from osv import osv, fields

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def _get_facturae_invoice_dict_data(self, cr, uid, ids, context={}):
        data2 = super(account_invoice, self)._get_facturae_invoice_dict_data(cr, uid, ids, context=context)
        data = data2
        comprobante = data[0]['Comprobante']
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
        dict_cfdi_comprobante.update({
            'cfdi:Comprobante' : {
            'cfdi:Emisor' : {'rfc' : rfc, 'nombre' : nombre, 'cfdi:DomicilioFiscal' : dom_Fiscal, 'cfdi:ExpedidoEn' : exp_en, 'cfdi:RegimenFiscal' : reg_Fiscal},
            'cfdi:Receptor' : {'rfc' : rfc_receptor, 'nombre' : nombre_receptor, 'cfdi:Domicilio' : domicilio_receptor},
            'cfdi:Conceptos' : [],
            'cfdi:Impuestos' : {'totalImpuestosTrasladados' : totalImpuestosTrasladados, 'cfdi:Traslados' : []},
        }})
        for concepto in comprobante['Conceptos']:
            dict_cfdi_comprobante['cfdi:Comprobante']['cfdi:Conceptos'].append(dict({'cfdi:Concepto' : concepto['Concepto']}))
        for traslado in comprobante['Impuestos']['Traslados']:
            dict_cfdi_comprobante['cfdi:Comprobante']['cfdi:Impuestos']['cfdi:Traslados'].append(dict({'cfdi:Traslado' : traslado['Traslado']}))
        print 'data2', data2
        print 'dict_cfdi_comprobante', dict_cfdi_comprobante
        return data2
    
    def ______get_facturae_invoice_dict_data(self, cr, uid, ids, context={}):
        invoices = self.browse(cr, uid, ids, context=context)
        invoice_tax_obj = self.pool.get("account.invoice.tax")
        invoice_datas = []
        invoice_data_parents = []
        for invoice in invoices:
            invoice_data_parent = {}
            if invoice.type == 'out_invoice':
                tipoComprobante = 'ingreso'
            elif invoice.type == 'out_refund':
                tipoComprobante = 'egreso'
            else:
                raise osv.except_osv(_('Warning !'), _('Solo se puede emitir factura electronica a clientes.!'))
                
            #Inicia seccion: Comprobante
            invoice_data_parent['cfdi:Comprobante'] = {}
            invoice_data_parent['cfdi:Comprobante'].update({
                'xmlns:cfdi' : "http://www.sat.gob.mx/cfd/3",
                'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                'xsi:schemaLocation': "http://www.sat.gob.mx/cfd/2 http://www.sat.gob.mx/sitio_internet/cfd/2/cfdv32.xsd",
                'version': "3.2",
            })
            number_work = invoice.number or invoice.internal_number
            invoice_data_parent['cfdi:Comprobante'].update({
                'folio': number_work,
                'fecha': invoice.date_invoice_tz and \
                    time.strftime('%Y-%m-%dT%H:%M:%S', time.strptime(invoice.date_invoice_tz, '%Y-%m-%d %H:%M:%S'))
                    or '',
                'tipoDeComprobante': tipoComprobante,
                'formaDePago': u'Pago en una sola exhibición',
                'noCertificado': '@',
                'sello': '@',
                'certificado': '@',
                'subTotal': "%.2f"%( invoice.amount_untaxed or 0.0),
                'descuento': "0",#Add field general
                'total': "%.2f"%( invoice.amount_total or 0.0),
            })
            folio_data = self._get_folio(cr, uid, [invoice.id], context=context)
            serie = folio_data.get('serie', False)
            if serie:
                invoice_data_parent['cfdi:Comprobante'].update({
                    'serie': serie,
                })
            partner_obj = self.pool.get('res.partner')
            address_invoice = invoice.address_issued_id or False
            address_invoice_parent = invoice.company_emitter_id and invoice.company_emitter_id.address_invoice_parent_company_id or False
            
            if not address_invoice:
                raise osv.except_osv(_('Warning !'), _('No se tiene definida la direccion emisora !'))
                
            if not address_invoice_parent:
                raise osv.except_osv(_('Warning !'), _('No se ha definido una compañia  !'))

            if not address_invoice_parent.vat:
                raise osv.except_osv(_('Warning !'), _('No se ha definido RFC para la direccion de factura de la compañia!'))
                
            invoice_data = invoice_data_parent['cfdi:Comprobante']
            invoice_data['cfdi:Emisor'] = {}
            invoice_data['cfdi:Emisor'].update({

                'rfc': ((address_invoice_parent._columns.has_key('vat_split') and address_invoice_parent.vat_split or address_invoice_parent.vat) or '').replace('-', ' ').replace(' ',''),
                'nombre': address_invoice_parent.name or '',
                #Obtener domicilio dinamicamente
                #virtual_invoice.append( (invoice.company_id and invoice.company_id.partner_id and invoice.company_id.partner_id.vat or '').replac

                'cfdi:DomicilioFiscal': {
                    'calle': address_invoice_parent.street and address_invoice_parent.street.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                    'noExterior': address_invoice_parent.l10n_mx_street3 and address_invoice_parent.l10n_mx_street3.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A', #"Numero Exterior"
                    'noInterior': address_invoice_parent.l10n_mx_street4 and address_invoice_parent.l10n_mx_street4.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A', #"Numero Interior"
                    'colonia':  address_invoice_parent.street2 and address_invoice_parent.street2.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A' ,
                    'localidad': address_invoice_parent.l10n_mx_city2 and address_invoice_parent.l10n_mx_city2.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A',
                    'municipio': address_invoice_parent.city and address_invoice_parent.city.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                    'estado': address_invoice_parent.state_id and address_invoice_parent.state_id.name and address_invoice_parent.state_id.name.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '' ,
                    'pais': address_invoice_parent.country_id and address_invoice_parent.country_id.name and address_invoice_parent.country_id.name.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')or '',
                    'codigoPostal': address_invoice_parent.zip and address_invoice_parent.zip.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                },
                'cfdi:ExpedidoEn': {
                    'calle': address_invoice.street and address_invoice.street.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                    'noExterior': address_invoice.l10n_mx_street3 and address_invoice.l10n_mx_street3.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A', #"Numero Exterior"
                    'noInterior': address_invoice.l10n_mx_street4 and address_invoice.l10n_mx_street4.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A', #"Numero Interior"
                    'colonia':  address_invoice.street2 and address_invoice.street2.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A' ,
                    'localidad': address_invoice.l10n_mx_city2 and address_invoice.l10n_mx_city2.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A',
                    'municipio': address_invoice.city and address_invoice.city.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                    'estado': address_invoice.state_id and address_invoice.state_id.name and address_invoice.state_id.name.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '' ,
                    'pais': address_invoice.country_id and address_invoice.country_id.name and address_invoice.country_id.name.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')or '',
                    'codigoPostal': address_invoice.zip and address_invoice.zip.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                },
            })
            #Termina seccion: Emisor
            
            #Inicia seccion: Receptor
            if not invoice.partner_id.vat:
                raise osv.except_osv(_('Warning !'), _('No se tiene definido el RFC del partner [%s].\n%s !')%(invoice.partner_id.name, msg2))
            if invoice.partner_id._columns.has_key('vat_split') and invoice.partner_id.vat[0:2] <> 'MX':
                rfc = 'XAXX010101000'
            else:
                rfc = ((invoice.partner_id._columns.has_key('vat_split') and invoice.partner_id.vat_split or invoice.partner_id.vat) or '').replace('-', ' ').replace(' ','')
            
            address_invoice_id = partner_obj.search(cr, uid, [('parent_id', '=', invoice.partner_id.id), ('type', '=', 'invoice')])
            if not address_invoice_id:
                raise osv.except_osv(_('Warning !'), _('No se ha definido una dirección de factura para el cliente'))
            address_invoice = partner_obj.browse(cr, uid, address_invoice_id[0], context=context)
            invoice_data['cfdi:Receptor'] = {}
            invoice_data['cfdi:Receptor'].update({
                'rfc': rfc,
                'nombre': (invoice.partner_id.name or ''),
                'cfdi:Domicilio': {
                    'calle': address_invoice.street and address_invoice.street.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                    'noExterior': address_invoice.l10n_mx_street3 and address_invoice.l10n_mx_street3.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A', #"Numero Exterior"
                    'noInterior': address_invoice.l10n_mx_street4 and address_invoice.l10n_mx_street4.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A', #"Numero Interior"
                    'colonia':  address_invoice.street2 and address_invoice.street2.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A' ,
                    'localidad': address_invoice.l10n_mx_city2 and address_invoice.l10n_mx_city2.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or 'N/A',
                    'municipio': address_invoice.city and address_invoice.city.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                    'estado': address_invoice.state_id and address_invoice.state_id.name and address_invoice.state_id.name.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '' ,
                    'pais': address_invoice.country_id and address_invoice.country_id.name and address_invoice.country_id.name.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')or '',
                    'codigoPostal': address_invoice.zip and address_invoice.zip.replace('\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') or '',
                },
            })
            #Termina seccion: Receptor
            #Inicia seccion: Conceptos
            invoice_data['cfdi:Conceptos'] = []
            for line in invoice.invoice_line:
                price_unit = line.quantity <> 0 and line.price_subtotal/line.quantity or 0.0
                concepto = {
                    'cantidad': "%.2f"%( line.quantity or 0.0),
                    'descripcion': line.name or '',
                    'valorUnitario': "%.2f"%( price_unit or 0.0),
                    'importe': "%.2f"%( line.price_subtotal or 0.0),#round(line.price_unit *(1-(line.discount/100)),2) or 0.00),#Calc: iva, disc, qty
                    ##Falta agregar discount
                }
                unidad = line.uos_id and line.uos_id.name or ''
                if unidad:
                    concepto.update({'unidad': unidad})
                product_code = line.product_id and line.product_id.default_code or ''
                if product_code:
                    concepto.update({'noIdentificacion': product_code})
                invoice_data['cfdi:Conceptos'].append( {'cfdi:Concepto': concepto} )

                pedimento = None
                try:
                    pedimento = line.tracking_id.import_id
                except:
                    pass
                if pedimento:
                    informacion_aduanera = {
                        'numero': pedimento.name or '',
                        'fecha': pedimento.date or '',
                        'aduana': pedimento.customs,
                    }
                    concepto.update( {'InformacionAduanera': informacion_aduanera} )
            #Termina seccion: Conceptos
            
            #Inicia seccion: impuestos
            invoice_data['cfdi:Impuestos'] = {}
            #~ invoice_data['Impuestos'].update({
                #'totalImpuestosTrasladados': "%.2f"%( invoice.amount_tax or 0.0),
            #~ })
            #~ invoice_data['cfdi:Impuestos'].update({
                #'totalImpuestosRetenidos': "%.2f"%( invoice.amount_tax or 0.0 )
            #~ })

            invoice_data_impuestos = invoice_data['cfdi:Impuestos']
            invoice_data_impuestos['cfdi:Traslados'] = []

            tax_names = []
            totalImpuestosTrasladados = 0
            totalImpuestosRetenidos = 0
            for line_tax_id in invoice.tax_line:
                tax_name = line_tax_id.name2
                tax_names.append( tax_name )
                line_tax_id_amount = abs( line_tax_id.amount or 0.0 )
                if line_tax_id.amount >= 0:
                    impuesto_list = invoice_data_impuestos['cfdi:Traslados']
                    impuesto_str = 'Traslado'
                    totalImpuestosTrasladados += line_tax_id_amount
                else:
                    impuesto_list = invoice_data_impuestos.setdefault('Retenciones', [])
                    impuesto_str = 'Retencion'
                    totalImpuestosRetenidos += line_tax_id_amount
                impuesto_dict = {impuesto_str:
                    {
                        'impuesto': tax_name,
                        'importe': "%.2f"%( line_tax_id_amount ),
                    }
                }
                if line_tax_id.amount >= 0:
                    impuesto_dict[impuesto_str].update({'tasa': "%.2f"%( abs( line_tax_id.tax_percent ) )})
                impuesto_list.append( impuesto_dict )

            invoice_data['cfdi:Impuestos'].update({
                'totalImpuestosTrasladados': "%.2f"%( totalImpuestosTrasladados ),
            })
            if totalImpuestosRetenidos:
                invoice_data['cfdi:Impuestos'].update({
                    'totalImpuestosRetenidos': "%.2f"%( totalImpuestosRetenidos )
                })

            tax_requireds = ['IVA', 'IEPS']
            for tax_required in tax_requireds:
                if tax_required in tax_names:
                    continue
                invoice_data_impuestos['cfdi:Traslados'].append( {'cfdi:Traslado': {
                    'impuesto': tax_required,
                    'tasa': "%.2f"%( 0.0 ),
                    'importe': "%.2f"%( 0.0 ),
                }} )
            #Termina seccion: impuestos
            
            invoice_data_parents.append( invoice_data_parent )
            invoice_data_parent['state'] = invoice.state
            invoice_data_parent['invoice_id'] = invoice.id
            invoice_data_parent['type'] = invoice.type
            invoice_data_parent['date_invoice'] = invoice.date_invoice
            invoice_data_parent['date_invoice_tz'] = invoice.date_invoice_tz
            invoice_data_parent['currency_id'] = invoice.currency_id.id

            date_ctx = {'date': invoice.date_invoice_tz and time.strftime('%Y-%m-%d', time.strptime(invoice.date_invoice_tz, '%Y-%m-%d %H:%M:%S')) or False}
            currency = self.pool.get('res.currency').browse(cr, uid, [invoice.currency_id.id], context=date_ctx)[0]
            rate = currency.rate <> 0 and 1.0/currency.rate or 0.0

            invoice_data_parent['rate'] = rate
            
        date_invoice_32 = invoice_data_parents_32[0].get('date_invoice',{}) and datetime.strptime( invoice_data_parents[0].get('date_invoice',{}), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d') or False
        if not date_invoice_32:
            raise osv.except_osv(_('Fecha de Factura vacía'),_('No se puede generar una factura sin fecha, asegurese que la factura no este en estado borrador y que la fecha a la factura no este vacía.'))
        if date_invoice_32 < '2012-07-01':
            return invoice_data_parent_32
        else:
            invoice = self.browse(cr, uid, ids, context={'date':date_invoice_32})[0]
            city = invoice_data_parents_32 and invoice_data_parents_32[0].get('cfdi:Comprobante',{}).get('cfdi:Emisor', {}).get('cfdi:ExpedidoEn',{}).get('municipio', {}) or False
            state = invoice_data_parents_32 and invoice_data_parents_32[0].get('cfdi:Comprobante',{}).get('cfdi:Emisor', {}).get('cfdi:ExpedidoEn',{}).get('estado', {}) or False
            country = invoice_data_parents_32 and invoice_data_parents_32[0].get('cfdi:Comprobante',{}).get('cfdi:Emisor', {}).get('cfdi:ExpedidoEn',{}).get('pais', {}) or False
            if city and state and country:
                address = city +' '+ state +', '+ country
            else:
                raise osv.except_osv(_('Domicilio Incompleto!'),_('Verifique que el domicilio de la compañia emisora del comprobante fiscal este completo (Ciudad - Estado - Pais)'))
            
            if not invoice.company_emitter_id.partner_id.regimen_fiscal_id.name:
                raise osv.except_osv(_('Regimen Fiscal Faltante!'),_('El Regimen Fiscal de la compañia emisora del comprobante fiscal es un dato requerido'))
            invoice_data_parents_32[0]['cfdi:Comprobante']['xsi:schemaLocation'] = 'http://www.sat.gob.mx/cfd/2 http://www.sat.gob.mx/sitio_internet/cfd/2/cfdv32.xsd'
            invoice_data_parents_32[0]['cfdi:Comprobante']['version'] = '3.2'
            invoice_data_parents_32[0]['cfdi:Comprobante']['TipoCambio'] = invoice.rate or 1
            invoice_data_parents_32[0]['cfdi:Comprobante']['Moneda'] = invoice.currency_id.name or ''
            invoice_data_parents_32[0]['cfdi:Comprobante']['NumCtaPago'] = invoice.acc_payment.last_acc_number or 'No identificado'
            invoice_data_parents_32[0]['cfdi:Comprobante']['metodoDePago'] = invoice.pay_method_id.name or 'No identificado'
            invoice_data_parents_32[0]['cfdi:Comprobante']['cfdi:Emisor']['cfdi:RegimenFiscal'] = {'Regimen':invoice.company_emitter_id.partner_id.regimen_fiscal_id.name or ''}
            invoice_data_parents_32[0]['cfdi:Comprobante']['LugarExpedicion'] = address
        
        return invoice_data_parents
        
    def _______________get_facturae_invoice_xml_data(self, cr, uid, ids, context={}):
        if not context:
            context = {}
        data_dict = self._get_facturae_invoice_dict_data(cr, uid, ids, context=context)[0]
        doc_xml = self.dict2xml( {'cfdi:Comprobante': data_dict.get('cfdi:Comprobante') } )
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

        if not data_dict['cfdi:Comprobante'].get('folio', ''):
            raise osv.except_osv(_('Error en Folio!'), _('No se pudo obtener el Folio del comprobante.\nAntes de generar el XML, de clic en el boton, generar factura.\nVerifique su configuracion.\n%s'%(msg2)) )

        #time.strftime('%Y-%m-%dT%H:%M:%S', time.strptime(invoice.date_invoice, '%Y-%m-%d %H:%M:%S'))
        context.update( { 'fecha': data_dict['cfdi:Comprobante']['fecha'] } )
        sign_str = self._get_sello(cr=False, uid=False, ids=False, context=context)
        if not sign_str:
            raise osv.except_osv(_('Error en Sello !'), _('No se pudo generar el sello del comprobante.\nVerifique su configuracion.\ns%s')%(msg2))

        nodeComprobante = doc_xml.getElementsByTagName("cfdi:Comprobante")[0]
        nodeComprobante.setAttribute("sello", sign_str)
        data_dict['cfdi:Comprobante']['sello'] = sign_str

        noCertificado = self._get_noCertificado( context['fname_cer'] )
        if not noCertificado:
            raise osv.except_osv(_('Error en No Certificado !'), _('No se pudo obtener el No de Certificado del comprobante.\nVerifique su configuracion.\n%s')%(msg2))
        nodeComprobante.setAttribute("noCertificado", noCertificado)
        data_dict['cfdi:Comprobante']['noCertificado'] = noCertificado

        cert_str = self._get_certificate_str( context['fname_cer'] )
        if not cert_str:
            raise osv.except_osv(_('Error en Certificado!'), _('No se pudo generar el Certificado del comprobante.\nVerifique su configuracion.\n%s')%(msg2))
        cert_str = cert_str.replace(' ', '').replace('\n', '')
        nodeComprobante.setAttribute("certificado", cert_str)
        data_dict['cfdi:Comprobante']['certificado'] = cert_str

        self.write_cfd_data(cr, uid, ids, data_dict, context=context)

        if context.get('type_data') == 'dict':
            return data_dict
        if context.get('type_data') == 'xml_obj':
            return doc_xml
        data_xml = doc_xml.toxml('UTF-8')
        data_xml = codecs.BOM_UTF8 + data_xml
        fname_xml = (data_dict['cfdi:Comprobante']['cfdi:Emisor']['rfc'] or '') + '.' + ( data_dict['cfdi:Comprobante'].get('serie', '') or '') + '.' + ( data_dict['cfdi:Comprobante'].get('folio', '') or '') + '.xml'
        data_xml = data_xml.replace ('<?xml version="1.0" encoding="UTF-8"?>','<?xml version="1.0" encoding="UTF-8"?>\n')
        return fname_xml, data_xml
            
account_invoice()
