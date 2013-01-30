<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    %for o in objects :
        ${set_global_data(o)}
        <div class="title">${o.company_emitter_id.address_invoice_parent_company_id.name or ''|entity}</div>
        <table>
            <tr>
                <td width="350" align="center">
                    ${helper.embed_image('jpeg',str(o.company_emitter_id.logo),200, 150)}
                </td>
                <td class="td_data_exp" width="700">
                    <div class="emitter">${_("Calle:")} ${o.company_emitter_id.address_invoice_parent_company_id.street or ''|entity}
                    ${_("Nro. Ext:")} ${o.company_emitter_id.address_invoice_parent_company_id.street3 or ''|entity}
                    ${_("Int:")} ${o.company_emitter_id.address_invoice_parent_company_id.street4 or ''|entity}
                    <br />${_("Colonia:")} ${o.company_emitter_id.address_invoice_parent_company_id.street2 or ''|entity}
                    <br />${_("Ciudad:")} ${o.company_emitter_id.address_invoice_parent_company_id.city or ''|entity} 
                    ${_("Estado:")} ${o.company_emitter_id.address_invoice_parent_company_id.state_id and o.company_emitter_id.address_invoice_parent_company_id.state_id.name or ''|entity}
                    <br />${_("Localidad:")} ${ o.company_emitter_id.address_invoice_parent_company_id.city2 or ''|entity}
                    <br />${_("CP:")} ${ o.company_emitter_id.address_invoice_parent_company_id.zip or ''|entity}
                    <br/>${_("RFC:")} ${ o.company_emitter_id.partner_id._columns.has_key('vat_split') and o.company_emitter_id.partner_id.vat_split or o.company_emitter_id.partner_id.vat|entity}
                    <br/>${_("Teléfono(s):")}
                    <br/>
                    ${o.company_emitter_id.address_invoice_parent_company_id.phone or ''|entity}
                    ${o.company_emitter_id.address_invoice_parent_company_id.fax or ''|entity}
                    ${o.company_emitter_id.address_invoice_parent_company_id.mobile or ''|entity}</div>
                </td>
                <td width="350">
                    <div class="folio">${_("Folio:")}
                    %if o.type in ['out_invoice', 'out_refund']:
                        %if o.state in ['open', 'paid', 'cancel']:
                            ${o.number or ''|entity}
                        %endif
                    %else:
                        ${'SIN FOLIO O ESTATUS NO VALIDO'}
                    %endif
                    </div>
                    %if o.state == 'cancel': 
                        ${'FACTURA CANCELADA' |entity} 
                    %endif
                    %if o.address_issued_id:
                        ${o.address_issued_id.city or ''|entity}
                        %if o.address_issued_id.state_id:
                            , ${o.address_issued_id.state_id.name or ''|entity}
                        %endif
                    %endif
                    <br/>${"a"} ${o.date_invoice_tz or ''|entity}
                    %if o.invoice_sequence_id.approval_id.type != 'cbb':
                    <div>${_("Serie:")} ${get_approval().serie or ''|entity}
                    <br/>${_("Aprobación:")} ${get_approval().approval_number or ''|entity}
                    <br/>${_("Año Aprobación:")} ${get_approval().approval_year or ''|entity}</div> 
                    %endif
                </td>
            </tr>
        </table>
        <table class="line" width="100%" border="1"></table>
        <table>
            <tr>
                <td class="address">
                    <font class="font" color="#280099"><b>Receptor</b></font>
                    <br/><font class="font">Nombre: ${o.partner_id.name or ''|entity}
                    <br/>Dirección: ${get_data_partner(o.partner_id)['street'] or ''|entity}
                    No. Ext: ${get_data_partner(o.partner_id)['street3'] or ''|entity}
                    Int: ${get_data_partner(o.partner_id)['street4'] or ''|entity}</font>
                    <br/><font class="font">Colonia: ${get_data_partner(o.partner_id)['street2'] or ''|entity}
                    <br/>Localidad: ${get_data_partner(o.partner_id)['city2'] or ''|entity}
                    <br/>C.P.: ${get_data_partner(o.partner_id)['zip'] or ''|entity}
                    <br/>R. F. C. : ${get_data_partner(o.partner_id)['vat'] or ''|entity}
                    <br/>Teléfono(s):
                    <br/>${get_data_partner(o.partner_id)['phone'] or ''|entity}
                    <br/>${get_data_partner(o.partner_id)['fax'] or ''|entity}
                    <br/>${get_data_partner(o.partner_id)['mobile'] or ''|entity}</font>
                </td>
                <td class="address">
                    <font class="font">Condición de pago:
                    %if o.payment_term:
                        <font class="font">${o.payment_term.note or o.payment_term.name or ''|entity}</font>
                    %endif
                    %if o.origin:
                        <br/><font class="font">Origen: ${o.origin or ''|entity}</font>
                    %endif
                    <br/><font class="font">Expedido en:</font>
                    %if o.address_issued_id:
                        <br/><font class="font">${o.address_issued_id.name or ''|entity}</font>
                        <br/><font class="font">Calle: ${o.address_issued_id.street or ''|entity}</font>
                        <font class="font">Nro. Ext: ${o.address_issued_id.street3 or ''|entity}</font>
                        <font class="font">Int: ${o.address_issued_id.street4 or ''|entity}</font>
                        <br/><font class="font">Colonia: ${o.address_issued_id.street2 or ''|entity}</font>
                        <br/><font class="font">Ciudad: ${o.address_issued_id.city or ''|entity}</font>
                        <br/><font class="font">Localidad: ${o.address_issued_id.city2 or ''|entity}</font>
                        <br/><font class="font">Estado: ${o.address_issued_id.state_id.name or ''|entity}</font>
                        <br/><font class="font">CP: ${o.address_issued_id.zip or ''|entity}</font>
                    %endif
                </td>
            </tr>
        </table>
        <table>
            <tr>
                <td width=90><b><font color="#280099">${_("Cant.")}</font></b></td>
                <td width=90><b><font color="#280099">${_("Unidad")}</font></b></td>
                <td width=400><b><font color="#280099">${_("Descripción")}</font></b></td>
                <td width=90><b><font color="#280099">${_("Clave")}</font></b></td>
                <td width=90><b><font color="#280099">${_("P.Unitario")}</font></b></td>
                <td width=90><b><font color="#280099">${_("Dto. %")}</font></b></td>
                <td width=90><b><font color="#280099">${_("Importe")}</font></b></td>
            </tr>
            %for l in o.invoice_line: 
                <tr>
                    <td width=90>${l.quantity}</td>
                    <td width=90>${l.uos_id.name or ''|entity}</td>
                    <td width=400>${l.name or ''|entity}</td>
                    <td width=90>${l.product_id.default_code or ''|entity}</td>
                    <td width=90>${formatLang(l.price_unit) or ''|entity}</td>
                    <td width=90>${formatLang(l.discount) or ''|entity} %</td>
                    <td width=90>${formatLang(l.price_subtotal) or ''|entity}</td>
                </tr>
            %endfor
        </table>
        <table align="right">
            <tr>
                <td>${_("Suma $:")}</td>
                <td>${get_sum_total(o.invoice_line) or 0.0 |entity}</td>
            </tr>
            <tr>
                <td>${_("Sub Total:")} $</td>
                <td>${formatLang(o.amount_untaxed) or ''|entity}</td>
            </tr>
            %for tax in get_taxes(): 
                <tr>
                    <td>${tax['name2']} ${round(float(tax['tax_percent']))} ${"% $"}</td>
                    <td>${formatLang(float( tax['amount'] ) ) or ''|entity}</td>
                </tr>
            %endfor
            %for tax_ret in get_taxes_ret():
                <tr>
                    <td>${tax_ret['name2']} ${"Ret"} ${round( float( tax_ret['tax_percent'] ), 2 )*-1 } ${"% $"}</td>
                    <td>${formatLang( float( tax_ret['amount'] )*-1 ) or ''|entity}</td>
                </tr>
            %endfor
            <tr align="left">
                <td>${_("Total:")} $</td>
                <td>${formatLang(o.amount_total) or ''|entity}</td>
            </tr>
        </table>
        <br clear="all" />
        <table align="left">
            <tr>
                <td>
                    <font class="font" color="#280099">${_("IMPORTE CON LETRA: ")}</font>
                    <br/><font class="font">${o.amount_to_text or ''|entity}</font>
                </td>
            </tr>
        </table>
        <br clear="all"/>
        <div>
            %if o.invoice_sequence_id.approval_id.type == 'cfd22':
                <font class="font">“Este documento es una representacion impresa de un CFD”
                <br/>CFD, Comprobante Fiscal Digital</font>
            %endif
            %if o.invoice_sequence_id.approval_id.type == 'cfdi32':
                <font class="font">“Este documento es una representacion impresa de un CFDI”
                <br/>CFDI, Comprobante Fiscal Digital por Internet</font>
                <br/>
                <table frame="box" rules="cols">
                    <tr>
                        <td width=300>
                            <font class="font">Certificado del emisor</font>
                        </td>
                        <td width=200>
                            <font class="font">Certificado del SAT</font>
                        </td>
                        <td width=200>
                            <font class="font">Fecha de Timbrado</font>
                        </td>
                        <td width=300>
                            <font class="font">Folio Fiscal</font>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <font class="font">${ o.no_certificado or ''|entity }</font>
                        </td>
                        <td>
                            <font class="font">${ o.cfdi_no_certificado or ''|entity }</font>
                        </td>
                        <td>
                            <font class="font">${ o.cfdi_fecha_timbrado or ''|entity }</font>
                        </td>
                        <td>
                            <font class="font">${ o.cfdi_folio_fiscal or ''|entity }</font>
                        </td>
                    </tr>
                </table>
                <br/>
            %endif
            %if o.invoice_sequence_id.approval_id.type != 'cbb':
                <table rules="all">
                    <tr>
                        <td class="reg_fis">
                            <font class="font"><b>Régimen Fiscal:</b></font>
                            <br/><font class="font">${ o.company_emitter_id.partner_id.regimen_fiscal_id.name or 'No identificado'|entity }</font>
                        </td>
                        <td class="reg_fis">
                            <font class="font"><b>Método de Pago:</b></font>
                            <br/><font class="font">${ o.company_emitter_id.partner_id.regimen_fiscal_id.name or 'No identificado'|entity }</font>
                        </td>
                        <td class="reg_fis">
                            <font class="font"><b>Últimos 4 dígitos de la cuenta bancaria:</b></font>
                            <br/><font class="font">${ o.acc_payment.last_acc_number or 'No identificado' }</font>
                        </td>
                    </tr>
                </table>
            %endif
        </div>
        <div>
            %if o.invoice_sequence_id.approval_id.type == 'cbb':
                <table frame="box">
                    <tr>
                        <td width="20%" valign="top" align="center">
                            %if get_approval():
                                ${helper.embed_image('jpeg',str(get_approval().cbb_image),170, 170)}
                            %endif
                        </td>
                        <td width="50%" valign="top" align="left">
                            <font class="font">Número de aprobación SICOFI: ${get_approval().approval_number or '' |entity}</font>
                            <br/><font class="font">Pago en una sola exhibición</font>
                            <br/><font class="font">La reproducción apócrifa de este comprobante constituye un delito en los términos de las disposiciones fiscales.</font>
                            <br/><font class="font">Este comprobante tendrá una vigencia de dos años contados a partir de la fecha aprobación de la asignación de folios, la cual es ${get_approval().date_start or '' |entity}</font>
                        </td>
                    </tr>
                </table>
            %endif
            %if o.invoice_sequence_id.approval_id.type == 'cfd22':
                <table frame="box">
                    <tr>
                        <td width="100%" valign="top" align="left">
                            <div><font class="facturae">Serie del Certificado :
                            <br/>${o.no_certificado or ''|entity}</font>
                            <br/><font class="facturae">Sello digital:
                            <br/>${split_string( o.sello or '') or ''|entity}</font>
                            </div>
                            <div align="center">
                                <font class="facturae">Cadena original :</font>
                                <br/><font class="facturae">${split_string( o.cadena_original or '') or '' |entity}</font>
                            </div>
                        </td>
                    </tr>
                </table>
            %endif
            %if o.invoice_sequence_id.approval_id.type == 'cfdi32':
                <table frame="box">
                    <tr>
                        <td width="80%" valign="top" align="left">
                            <font class="facturae"><b>Sello Digital Emisor:</b>
                            <br/>${split_string( o.sello ) or ''|entity}</font>
                            <br/><font class="facturae"><b>Sello Digital SAT:</b>
                            <br/>${split_string( o.cfdi_sello or '') or ''|entity}</font>
                            <br/><font class="facturae"><b>Cadena original:</b></font>
                            <br/><font class="facturae">${split_string( o.cadena_original ) or '' |entity}</font>
                        </td>
                        <td width="20%" valign="top" align="center">
                            ${helper.embed_image('jpeg',str(o.cfdi_cbb),200, 200)}
                        </td>
                    </tr>
                </table>
            %endif
        </div>
    %endfor
</body>
</html>
