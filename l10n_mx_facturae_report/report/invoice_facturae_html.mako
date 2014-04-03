<!DOCTYPE>
<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    %for o in objects :
        ${set_global_data(o)}
        <table class="basic_table">
            <tr>
                <td style="vertical-align: top;">
                    ${helper.embed_image('jpeg',str(o.company_emitter_id.logo),180, 85)}
                </td>
                <td>
                    <table class="basic_table">
                        <tr>
                            <td width='50%'>
                                <div class="title">${o.company_emitter_id.address_invoice_parent_company_id.name or ''|entity}</div>
                            </td>
                            <td width='20%'>
                                %if o.type == 'out_invoice':
                                    <div class="invoice">${_("Factura:")}
                                %elif o.type == 'out_refund':
                                    <div class="refund">${_("NOTA DE CREDITO:")}
                                %endif
                                %if o.type in ['out_invoice', 'out_refund']:
                                    %if o.state in ['open', 'paid', 'cancel']:
                                        ${o.number or ''|entity}
                                    %else:
                                        <font size="2">${'SIN FOLIO O ESTATUS NO VALIDO'}</font>
                                    %endif
                                %endif
                                %if o.state == 'cancel':
                                    ${'FACTURA CANCELADA' |entity}
                                %endif
                            </td>
                        </tr>
                        <tr>
                            <td class="td_data_exp">
                                <div class="emitter">
                                    %if o.company_emitter_id:
                                        %if o.company_emitter_id.address_invoice_parent_company_id:
                                            <%
                                            if o.company_emitter_id.address_invoice_parent_company_id.use_parent_address:
                                                address_emitter = o.company_emitter_id.address_invoice_parent_company_id.parent_id
                                            else:
                                                address_emitter = o.company_emitter_id.address_invoice_parent_company_id%>
                                            <br/>${address_emitter.street or ''|entity}
                                            ${address_emitter.l10n_mx_street3 or ''|entity}
                                            ${address_emitter.l10n_mx_street4 or ''|entity}
                                            ${address_emitter.street2 or ''|entity}
                                            ${address_emitter.zip or ''|entity}
                                            <br/>${_("Localidad:")} ${address_emitter.l10n_mx_city2 or ''|entity}
                                            <br/>${address_emitter.city or ''|entity}
                                            , ${address_emitter.state_id and address_emitter.state_id.name or ''|entity}
                                            , ${address_emitter.country_id and address_emitter.country_id.name or ''|entity}
                                            <br/><b>${_("RFC:")} ${ o.company_emitter_id.partner_id._columns.has_key('vat_split') and o.company_emitter_id.partner_id.vat_split or o.company_emitter_id.partner_id.vat or ''|entity}</b>
                                            %if o.company_emitter_id.partner_id.regimen_fiscal_id:
                                                <br/>${ o.company_emitter_id.partner_id.regimen_fiscal_id.name or ''|entity }
                                            %endif
                                            <br/>${_("Tel&eacute;fono(s):")}
                                            ${address_emitter.phone or ''|entity}
                                            ${address_emitter.fax  and ',' or ''|entity} ${address_emitter.fax or ''|entity}
                                            ${address_emitter.mobile and ',' or ''|entity} ${address_emitter.mobile or ''|entity}
                                        %endif
                                    %endif
                                </div>
                            </td>
                            <td class="td_data_exp">
                                <div class="fiscal_address">
                                    %if o.payment_term.name:
                                        Condición de pago: ${o.payment_term.note or o.payment_term.name or ''|entity}
                                    %endif
                                    %if o.address_issued_id:
                                    <br/>Expedido en:
                                        ${o.address_issued_id.name or ''|entity}
                                        <br/>${o.address_issued_id.street or ''|entity}
                                        ${o.address_issued_id.l10n_mx_street3 or ''|entity}
                                        ${o.address_issued_id.l10n_mx_street4 or ''|entity}
                                        <br/>${o.address_issued_id.street2 or ''|entity}
                                        ${o.address_issued_id.zip or ''|entity}
                                        <br/>Localidad: ${o.address_issued_id.l10n_mx_city2 or ''|entity}
                                        <br/>${o.address_issued_id.city or ''|entity}
                                        ${o.address_issued_id.state_id.name and ',' or ''|entity} ${o.address_issued_id.state_id and o.address_issued_id.state_id.name or ''|entity}
                                        ${o.address_issued_id.country_id.name and ',' or ''|entity} ${o.address_issued_id.country_id and o.address_issued_id.country_id.name or ''|entity}
                                    %endif
                                <div/>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        <table class="line" width="100%" border="1"></table>
        <table class="basic_table" style="font-size:11;">
            <tr>
                <td width="80%">
                    <%res_client=get_data_partner(o.partner_id)%>
                    <table class="basic_table">
                        <tr>
                            <td class="cliente"><b>Receptor:</b></td>
                            <td width="64%" class="cliente">${res_client['name'] or ''|entity}</td>
                            <td class="cliente"><b>R. F. C.:</b></td>
                            <td width="16%" class="cliente"><b>${res_client['vat'] or ''|entity}</b></td>
                        </tr>
                    </table>
                    <table class="basic_table">
                        <tr>
                            <td width="7%" class="cliente"><b>Calle:</b></td>
                            <td class="cliente">${res_client['street'] or ''|entity}</td>
                            %if res_client['l10n_mx_street3']:
                                <td width="9%" class="cliente"><b>No. Ext:</b></td>
                                <td width="9%" class="cliente">${res_client['l10n_mx_street3'] or ''|entity}</td>
                            %endif
                            %if res_client['l10n_mx_street4']:
                                <td width="9%" class="cliente"><b>No. Int:</b></td>
                                <td width="9%" class="cliente">${res_client['l10n_mx_street4'] or ''|entity}</td>
                            %endif
                        </tr>
                    </table>
                    <table class="basic_table">
                        <tr>
                            <td width="10%" class="cliente"><b>Colonia:</b></td>
                            <td class="cliente">${res_client['street2'] or ''|entity}</td>
                            <td width="7%" class="cliente"><b>C.P.:</b></td>
                            <td class="cliente">${res_client['zip'] or ''|entity}</td>
                            %if res_client['l10n_mx_city2']:
                                <td width="12%" class="cliente"><b>Localidad:</b></td>
                                <td class="cliente">${res_client['l10n_mx_city2'] or ''|entity}</td>
                            %endif
                        </tr>
                    </table>
                    <table class="basic_table">
                        <tr>
                            <td width="9%" class="cliente"><b>Lugar:</b></td>
                            <td class="cliente">
                                ${res_client['city'] or ''|entity},
                                ${res_client['state'] or ''|entity},
                                ${res_client['country'] or ''|entity}
                            </td>
                        </tr>
                    </table>
                    <table class="basic_table" style="border-bottom:1px solid #002966;">
                        <tr>
                            <td width="13%" class="cliente"><b>Telefono(s):</b></td>
                            <td width="55%" class="cliente">
                                ${res_client['phone'] or ''|entity}
                                ${res_client['fax'] and ',' or ''|entity}
                                ${res_client['fax'] or ''|entity}
                                ${res_client['mobile'] and ',' or ''|entity}
                                ${res_client['mobile'] or ''|entity}</font>
                            <td width="9%" class="cliente"><b>Origen:</b></td>
                            <td width="23%" class="cliente"><b>${o.origin or ''|entity}</b></td>
                        </tr>
                    </table>
                </td>
                <td width="1%"></td>
                <td width="19%" align="center">
                    %if o.address_issued_id:
                        ${o.address_issued_id.city or ''|entity},
                        ${o.address_issued_id.state_id and o.address_issued_id.state_id.name or ''|entity},
                        ${o.address_issued_id.country_id and o.address_issued_id.country_id.name or ''|entity}
                    %endif
                    <br/>${_("a")} ${o.date_invoice_tz or ''|entity}
                    %if o.invoice_sequence_id.approval_id and o.invoice_sequence_id.approval_id.type != 'cbb':
                        ${_("Serie:")} ${o.invoice_sequence_id.approval_id.serie or _("Sin serie")|entity}
                        <br/>${_("Aprobaci&oacute;n:")} ${o.invoice_sequence_id.approval_id.approval_number or _("Sin aprobaci&oacute;n")|entity}
                        <br/>${_("A&ntilde;o Aprobaci&oacute;n:")} ${o.invoice_sequence_id.approval_id.approval_year or _("No v&aacute;lido")|entity}
                    %endif
                </td>
            </tr>
        </table>
        <br/>
        <table class="basic_table" style="color:#121212">
            <tr class="firstrow">
                <th width="10%">${_("Cant.")}</th>
                <th width="10%">${_("Unidad")}</th>
                <th>${_("Descripci&oacute;n")}</th>
                <th width="9%" >${_("P.Unitario")}</th>
                %if has_disc(o.invoice_line):
                    <th width="8%" >${_("Dto. %") or ''}</th>
                %endif
                <th width="15%">${_("Importe")}</th>
            </tr>
            <%row_count = 1%>
            %for line in o.invoice_line:
                %if (row_count%2==0):
                    <tr  class="nonrow">
                %else:
                    <tr>
                %endif
                    <td width="10%" class="number_td">${line.quantity or '0.0'}</td>
                    <td width="10%" class="basic_td">${line.uos_id.name or ''|entity}</td>
                    <td class="basic_td">${line.name or ''|entity}</td>
                    <td width="9%" class="number_td">$ ${formatLang(line.price_unit) or '0.0'|entity}</td>
                    %if has_disc(o.invoice_line):
                        <td width="8%" class="number_td">${formatLang(line.discount) or ''|entity} %</td>
                    %endif
                    <td width="15%" class="number_td">$ ${formatLang(line.price_subtotal) or '0.0'|entity}</td>
                </tr>
                <%row_count+=1%>
            %endfor
        </table>
        <table align="right" width="30%" style="border-collapse:collapse">
            %if get_taxes() or get_taxes_ret():
                <tr>
                    <td class="total_td">${_("Sub Total:")}</td>
                    <td align="right" class="total_td">$ ${formatLang(o.amount_untaxed) or ''|entity}</td>
                </tr>
            %endif
            %for tax in get_taxes():
                <tr>
                    <td class="tax_td">${tax['name2']} (${round(float(tax['tax_percent']))}) % </td>
                    <td class="tax_td" align="right">$ ${formatLang(float( tax['amount'] ) ) or ''|entity}</td>
                </tr>
            %endfor
            %for tax_ret in get_taxes_ret():
                <tr>
                    <td class="tax_td">${tax_ret['name2']} ${_("Ret")} ${round( float( tax_ret['tax_percent'] ), 2 )*-1 } % </td>
                    <td class="tax_td" align="right">$ ${formatLang( float( tax_ret['amount'] )*-1 ) or ''|entity}</td>
                </tr>
            %endfor
            <tr align="left">
                <td class="total_td"><b>${_("Total:")}</b></td>
                <td class="total_td" align="right"><b>$ ${formatLang(o.amount_total) or ''|entity}</b></td>
            </tr>
        </table>
        <br clear="all" />
        <table class="basic_table">
            <tr>
                <td class="tax_td">
                    ${_("IMPORTE CON LETRA:")}
                </td>
            </tr>
            <tr>
                <td class="center_td">
                    <i>${o.amount_to_text or ''|entity}</i>
                </td>
            </tr>
            <tr>
                <td class="center_td">
                    ${_('PAGO EN UNA SOLA EXHIBICI&Oacute;N - EFECTOS FISCALES AL PAGO')}
                </td>
            </tr>
            
        </table>
        <br/>${o.comment or '' |entity}<br/>
        <br clear="all"/>
        <!--code for cfd-->
        %if 'cfdi' in o.invoice_sequence_id.approval_id.type:
            <font class="font">“Este documento es una representación impresa de un CFDI”
            <br/>CFDI, Comprobante Fiscal Digital por Internet</font>
        %elif 'cfd' in o.invoice_sequence_id.approval_id.type:
            ${_('&quot;Este documento es una representaci&oacute;n impresa de un CFD&quot;')}<br/>
            ${_('CFD, Comprobante Fiscal Digital')}
        %endif
        <!-- bank info-->
        %if o.company_emitter_id.partner_id.bank_ids:
            <table class="basic_table">
                <tr>
                    <td class="center_td">
                        ${_('Datos Bancarios')} ${o.company_emitter_id.address_invoice_parent_company_id.name or ''|entity}
                    </td>
                </tr>
            </table>
            <table class="basic_table" rules="all">
                <tr>
                    <td class="data_bank_label">${_('Banco / Moneda')}</td>
                    <td class="data_bank_label">${_('N&uacute;mero de cuenta')}</td>
                    <td class="data_bank_label" width="30%">${_('Clave Interbancaria Estandarizada (CLABE)')}</td>
                    <td class="data_bank_label">${_('Referencia')}</td>
                </tr>
                %for f in o.company_emitter_id.partner_id.bank_ids:
                    <tr>
                        <td class="center_td">${f.bank.name or ''|entity} ${f.currency2_id and '/' or '' |entity} ${f.currency2_id and f.currency2_id.name or '' |entity}</td>
                        <td class="center_td">${f.acc_number or ''|entity}</td>
                        <td class="center_td">${f.clabe or ''|entity}</td>
                        <td class="center_td">${f.reference or ''|entity}</td>
                    </tr>
                %endfor
            </table>
        %endif
        <!--code for cfd 3.2-->
        %if 'cfdi' in o.invoice_sequence_id.approval_id.type:
            <table class="basic_table" rules="cols" style="border:1.5px solid grey;">
                <tr>
                    <th width="33%"> ${_('Certificado del SAT')}</th>
                    <th> ${_('Fecha de Timbrado')}</th>
                    <th width="33%"> ${_('Folio Fiscal')}</th>
                </tr>
                <tr>
                    <td width="33%" class="center_td"> ${ o.cfdi_no_certificado or 'No identificado'|entity }</td>
                    <td width="34%" class="center_td"> ${ o.cfdi_fecha_timbrado or 'No identificado'|entity }</td>
                    <td width="33%" class="center_td"> ${ o.cfdi_folio_fiscal or 'No identificado'|entity }</td>
                </tr>
            </table>
        %endif
        <!--code for ! cbb-->
        %if o.invoice_sequence_id.approval_id.type != 'cbb' and o.invoice_sequence_id.approval_id.type != None:
            <table class="basic_table" rules="cols" style="border:1.5px solid grey;">
                <tr>
                    <th width="33%">${_('Certificado del emisor')}</th>
                    <th width="34%">${_('M&eacute;todo de Pago')}</th>
                    <th width="33%">${_('&Uacute;ltimos 4 d&iacute;gitos de la cuenta bancaria')}</th>
                </tr>
                <tr>
                    <td class="center_td">${ o.no_certificado or 'No identificado'|entity }</td>
                    <td class="center_td">${ o.pay_method_id.name or 'No identificado'|entity }</td>
                    <td class="center_td">
                        ${ o.acc_payment and o.acc_payment.bank_name or '' }
                        ${ o.acc_payment.last_acc_number or 'No identificado' }</td>
                </tr>
            </table>
        %endif
        <!--code for cbb-->
        %if o.invoice_sequence_id.approval_id and o.invoice_sequence_id.approval_id.type == 'cbb':
            <table class="basic_table" style="page-break-inside:avoid; border:1.5px solid grey;">
                <tr>
                    <td width="20%" valign="top">
                        %if ( o.type  in ['out_invoice', 'out_refund'] ) and ( o.state in ['open', 'paid', 'cancel'] ):
                            ${helper.embed_image('jpeg',str(o.invoice_sequence_id.approval_id.cbb_image),180, 180)}
                        %else:
                            <p> ${_('SIN FOLIO O ESTATUS NO VALIDO')}
                        %endif
                    </td>
                    <td valign="top" class="tax_td" style="padding-top:3px;">
                        %if ( o.type  in ['out_invoice', 'out_refund'] ) and ( o.state in ['open', 'paid', 'cancel'] ):
                            Número de aprobación SICOFI: ${o.invoice_sequence_id.approval_id.approval_number or '' |entity}<br/>
                        %else:
                            <p> ${_('SIN FOLIO O ESTATUS NO VALIDO')}</br>
                        %endif
                        La reproducción apócrifa de este comprobante constituye un delito en los términos de las disposiciones fiscales.<br/>
                        Este comprobante tendrá una vigencia de dos años contados a partir de la fecha aprobación de la asignación de folios, la cual es: ${o.invoice_sequence_id.approval_id.date_start or '' |entity}
                    </td>
                    <td width="15%" valign="top">
                        ${helper.embed_image('jpeg',str(o.company_emitter_id.cif_file),140, 220)}
                    </td>
                </tr>
            </table>
        <!--%else:
            <p> ${_('La aprobaci&oacute;n CBB no pudo ser obtenida, por favor contacte a su administrador')}
        -->
        %endif
        <!--code for cfd22-->
        %if o.invoice_sequence_id.approval_id.type == 'cfd22':
            <div style="page-break-inside:avoid; border:1.5px solid grey;">
                <table>
                    <tr>
                        <td>
                            <div class="float_left">${helper.embed_image('jpeg',str(o.company_emitter_id.cif_file),140, 220)}</div>
                            <span class="datos_fiscales">
                                <b>${_('Serie del Certificado')}</b><br/>
                                ${o.no_certificado or ''|entity}
                                <br/><br/><b>${_('Sello digital')}:</b><br/>
                                ${split_string( o.sello or '') or ''|entity}
                                <br/><br/><b>${_('Cadena original')}:</b><br/>
                                ${split_string( o.cadena_original or '') or '' |entity}
                            </td>
                        </tr>
                </table>
                </span>
            </div>
        %endif
        <!--code for cfd32-->
        %if 'cfdi' in o.invoice_sequence_id.approval_id.type:
            <div style="page-break-inside:avoid; border:1.5px solid grey;">
                <table width="100%" class="datos_fiscales">
                    <tr>
                        %if o.company_emitter_id.cif_file:
                        <td align="left">
                            ${helper.embed_image('jpeg',str(o.company_emitter_id.cif_file), 140, 220)}
                        </td>
                        %endif
                        <td valign="top" align="left">
                            %if o.company_emitter_id.cif_file == False:
                                <p class="cadena_without_cif">
                            %elif o.cfdi_cbb == False:
                                <p class="cadena_without_cbb">
                            %elif o.cfdi_cbb == False and o.company_emitter_id.cif_file == False:
                                <p class="cadena_without_cbb_cfd">
                            %elif o.cfdi_cbb and o.company_emitter_id.cif_file:
                                <p class="cadena_with_cbb_cfd">
                            %endif
                            <b>${_('Sello Digital Emisor:')} </b><br/>
                            ${split_string( o.sello ) or ''|entity}<br/>
                            <b>${_('Sello Digital SAT:')} </b><br/>
                            ${split_string( o.cfdi_sello or '') or ''|entity}<br/>
                            <b>${_('Cadena original:')} </b><br/>
                            ${split_string(o.cfdi_cadena_original) or ''|entity}</br>
                            <b>${_('Enlace al certificado: ')}</b></br>
                            ${o.pac_id and o.pac_id.certificate_link or ''|entity}</p>
                        </td>
                        %if o.cfdi_cbb:
                        <td align="right">
                            ${helper.embed_image('jpeg',str(o.cfdi_cbb), 180, 180)}
                        </td>
                        %endif
                    </tr>
                </table>
                <!--</span> si se activan, forzan un brinco de linea-->
            </div>
        %endif
        %if not o.invoice_sequence_id.approval_id.type:
            <hr>
            ${_('No se encontr&oacute; la aprobaci&oacute;n')}
            <hr>
        %endif
        <br></br>
        <section>
            %if o.company_id.dinamic_text:
                <table class="basic_table" style="border:1.5px solid grey;">
                    <tr><td class="address"><pre style='pre'>${ get_text_promissory(o.company_id, o.partner_id, address_emitter, o) or ''|entity }</pre></td></tr>
                </table>
            %endif
        </section>
    <p style="page-break-after:always"></p>
    %endfor

</body>
</html>
