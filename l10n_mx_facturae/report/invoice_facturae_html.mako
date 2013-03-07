<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    %for o in objects :
        ${set_global_data(o)}
        <table width="100%">
            <tr>
                <td width="20%"></td>
                <td width="60%">
                    <div class="title">${o.company_emitter_id.address_invoice_parent_company_id.name or ''|entity}</div>
                </td>
                <td width="20%">
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
                    </div>
                    %if o.state == 'cancel': 
                        ${'FACTURA CANCELADA' |entity} 
                    %endif
                </td>
            </tr>
        </table>
        <table width="100%">
            <tr>
                <td width="25%" align="center">
                    ${helper.embed_image('jpeg',str(o.company_emitter_id.logo),120, 120)}
                </td>
                <td class="td_data_exp" width="50%">
                    <div class="emitter">
                        %if o.company_emitter_id:
                            %if o.company_emitter_id.address_invoice_parent_company_id:
                                <br/>${o.company_emitter_id.address_invoice_parent_company_id.street or ''|entity}
                                ${o.company_emitter_id.address_invoice_parent_company_id.l10n_mx_street3 or ''|entity}
                                ${o.company_emitter_id.address_invoice_parent_company_id.l10n_mx_street4 or ''|entity}
                                ${o.company_emitter_id.address_invoice_parent_company_id.street2 or ''|entity}
                                ${ o.company_emitter_id.address_invoice_parent_company_id.zip or ''|entity}
                                <br />${_("Localidad:")} ${ o.company_emitter_id.address_invoice_parent_company_id.l10n_mx_city2 or ''|entity}
                                <br/>${o.company_emitter_id.address_invoice_parent_company_id.city or ''|entity} 
                                , ${o.company_emitter_id.address_invoice_parent_company_id.state_id and o.company_emitter_id.address_invoice_parent_company_id.state_id.name or ''|entity}
                                , ${o.company_emitter_id.address_invoice_parent_company_id.country_id and o.company_emitter_id.address_invoice_parent_company_id.country_id.name or ''|entity}
                                <br/><b>${_("RFC:")} ${ o.company_emitter_id.partner_id._columns.has_key('vat_split') and o.company_emitter_id.partner_id.vat_split or o.company_emitter_id.partner_id.vat or ''|entity}</b>
                                %if o.company_emitter_id.partner_id.regimen_fiscal_id:
                                    <br/>${ o.company_emitter_id.partner_id.regimen_fiscal_id.name or ''|entity }
                                %endif
                                <br/>${o.company_emitter_id.address_invoice_parent_company_id.phone and _("Teléfono(s):") or o.company_emitter_id.address_invoice_parent_company_id.fax and _("Teléfono(s):") or o.company_emitter_id.address_invoice_parent_company_id.mobile and _("Teléfono(s):") or ''|entity}
                                ${o.company_emitter_id.address_invoice_parent_company_id.phone or ''|entity}
                                ${o.company_emitter_id.address_invoice_parent_company_id.fax  and ',' or ''|entity} ${o.company_emitter_id.address_invoice_parent_company_id.fax or ''|entity}
                                ${o.company_emitter_id.address_invoice_parent_company_id.mobile and ',' or ''|entity} ${o.company_emitter_id.address_invoice_parent_company_id.mobile or ''|entity}
                            %endif
                        %endif
                    </div>
                </td>
                <td class="td_data_exp" width="25%">
                    <div class="fiscal_address">
                        %if o.payment_term.name:
                            Condición de pago: ${o.payment_term.note or o.payment_term.name or ''|entity}
                        %endif
                        %if o.address_issued_id:
                        <br/>Expedido en:
                            <br/>${o.address_issued_id.name or ''|entity}
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
        <table class="line" width="100%" border="1"></table>
        <font size="15"></font>
        <table style="font-size:11;">
            <tr>
                <td width="80%">
                    <%res_client=get_data_partner(o.partner_id)%>
                    <table class="table_cliente">
                        <tr>
                            <td class="cliente"><b>Receptor:</b></td>
                            <td width="64%" class="cliente">${o.partner_id.name or ''|entity}</td>
                            <td class="cliente"><b>R. F. C.:</b></td>
                            <td width="16%" class="cliente"><b>${res_client['vat'] or ''|entity}SMA010116FC4</b></td>
                        </tr>
                    </table>
                    <table class="table_cliente">
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
                    <table class="table_cliente">
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
                    <table class="table_cliente">
                        <tr>
                            <td width="9%" class="cliente"><b>Lugar:</b></td>
                            <td class="cliente">
                                ${res_client['city'] or ''|entity}, 
                                ${res_client['state'] or ''|entity},
                                ${res_client['country'] or ''|entity}
                            </td>
                        </tr>
                    </table>
                    <table class="table_cliente" style="border-bottom:1px solid #002966;">
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
                    %if o.invoice_sequence_id.approval_id.type != 'cbb':
                        ${_("Serie:")} ${get_approval() and get_approval().serie or _("Sin serie")|entity}
                        <br/>${_("Aprobación:")} ${get_approval() and get_approval().approval_number or _("Sin aprobación")|entity}
                        <br/>${_("Año Aprobación:")} ${get_approval() and get_approval().approval_year or _("No válido")|entity}
                    %endif
                </td>
            </tr>
        </table>
        <br/>
        <table style="border-collapse:collapse" width="100%">
            <tr class="firstrow">
                <th width="10%">${_("Cant.")}</th>
                <th width="10%">${_("Unidad")}</th>
                <th>${_("Descripción")}</th>
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
        <table align="left" width="100%">
            <tr>
                <td align="left" width="100%">
                    <font size="1">IMPORTE CON LETRA:</font>
                </td>
            </tr>
            <tr>
                <td align="center" width="100%">
                    <font size="1"><i>${o.amount_to_text or ''|entity}</i></font>
                </td>
            </tr>
            <tr>
                <td align="center" width="100%">
                    <font size="1">${_('PAGO EN UNA SOLA EXHIBICIÓN - EFECTO FISCAL AL PAGO')}</font>
                </td>
            </tr>
        </table>
        <br clear="all"/>
        <div>
            %if o.invoice_sequence_id.approval_id.type == 'cfd22':
                <font class="font">“Este documento es una representacion impresa de un CFD”
                <br/>CFD, Comprobante Fiscal Digital</font>
            %elif o.invoice_sequence_id.approval_id.type == 'cfdi32':
                <font class="font">“Este documento es una representacion impresa de un CFDI”
                <br/>CFDI, Comprobante Fiscal Digital por Internet</font>
            %endif
            %if o.company_emitter_id.partner_id.bank_ids:
                <div>
                    <table rules="all" width="100%">
                        <tr>
                            <td>
                                <div class="title_data_bank">${_('Datos Bancarios')} ${o.company_emitter_id.address_invoice_parent_company_id.name or ''|entity}</div>
                            </td>
                        </tr>
                    </table>
                    <table rules="all" width="100%">
                        <tr>
                            <td width="33%" class="data_bank_label"><b>Banco / Moneda</b></td>
                            <td width="34%" class="data_bank_label"><b>Número de cuenta</b></td>
                            <td width="33%" class="data_bank_label"><b>Clave Interbancaria Estandarizada (CLABE)</b></td>
                        </tr>
                        %for f in o.company_emitter_id.partner_id.bank_ids:
                            <tr>
                                <td width="33%" class="data_bank">${f.bank.name or ''|entity} ${f.currency2_id and '/' or '' |entity} ${f.currency2_id and f.currency2_id.name or '' |entity}</td>
                                <td width="34%" class="data_bank">${f.acc_number or ''|entity}</td>
                                <td width="33%" class="data_bank">${f.clabe or ''|entity}</td>
                            </tr>
                        %endfor
                    </table>
                </div>
            %endif
            <table width="100%">
                <tr><td align="center"><font size="1">${ o.company_emitter_id.promissory or ''|entity }</font></td></tr>
            </table>
            %if o.invoice_sequence_id.approval_id.type == 'cfdi32':
                <table frame="box" rules="cols" width="100%">
                    <tr>
                        <td width="33%" class="reg_fis">
                            <font class="font"><b>Certificado del SAT</b></font>
                        </td>
                        <td width="34%" class="reg_fis">
                            <font class="font"><b>Fecha de Timbrado</b></font>
                        </td>
                        <td width="33%" class="reg_fis">
                            <font class="font"><b>Folio Fiscal</b></font>
                        </td>
                    </tr>
                    <tr>
                        <td width="33%" class="reg_fis">
                            <font class="font">${ o.cfdi_no_certificado or ''|entity }</font>
                        </td>
                        <td width="34%" class="reg_fis">
                            <font class="font">${ o.cfdi_fecha_timbrado or ''|entity }</font>
                        </td>
                        <td width="33%" class="reg_fis">
                            <font class="font">${ o.cfdi_folio_fiscal or ''|entity }</font>
                        </td>
                    </tr>
                </table>
            %endif
            %if o.invoice_sequence_id.approval_id.type != 'cbb':
                <table rules="all" width="100%">
                    <tr>
                        <td width="33%" class="reg_fis">
                            <font class="font"><b>Certificado del emisor</b></font>
                            <br/><font class="font">${ o.no_certificado or 'No identificado'|entity }</font>
                        </td>
                        <td width="34%" class="reg_fis">
                            <font class="font"><b>Método de Pago:</b></font>
                            <br/><font class="font">${ o.company_emitter_id.partner_id.regimen_fiscal_id.name or 'No identificado'|entity }</font>
                        </td>
                        <td width="33%" class="reg_fis">
                            <font class="font"><b>Últimos 4 dígitos de la cuenta bancaria:</b></font>
                            <br/><font class="font">${ o.acc_payment.last_acc_number or 'No identificado' }</font>
                        </td>
                    </tr>
                </table>
            %endif
        </div>
        %if o.invoice_sequence_id.approval_id.type == 'cbb':
            <table frame="box">
                <tr>
                    <td width="20%" valign="top" align="center">
                        %if get_approval():
                            ${helper.embed_image('jpeg',str(get_approval().cbb_image),180, 180)}
                        %endif
                    </td>
                    <td width="70%" valign="top" align="left">
                        <font class="font">Número de aprobación SICOFI: ${get_approval() and get_approval().approval_number or '' |entity}</font>
                        <br/><font class="font">La reproducción apócrifa de este comprobante constituye un delito en los términos de las disposiciones fiscales.</font>
                        <br/><font class="font">Este comprobante tendrá una vigencia de dos años contados a partir de la fecha aprobación de la asignación de folios, la cual es ${get_approval() and get_approval().date_start or '' |entity}</font>
                    </td>
                    <td width="15%" valign="top" align="center">
                        ${helper.embed_image('jpeg',str(o.company_emitter_id.cif_file),140, 220)}
                    </td>
                </tr>
            </table>
        %endif
        %if o.invoice_sequence_id.approval_id.type == 'cfd22':
            <table frame="box" width="100%">
                <tr>
                    <td width="15%" valign="top" align="center">
                        ${helper.embed_image('jpeg',str(o.company_emitter_id.cif_file),140, 220)}
                    </td>
                    <td width="85%" valign="top">
                        <div><font class="facturae"><b>Serie del Certificado :</b></font>
                        <p class="cadena_cfd">${o.no_certificado or ''|entity}</p></div>
                        <div><font class="facturae"><b>Sello digital:</b></font>
                        <p class="cadena_cfd">${split_string( o.sello or '') or ''|entity}</p></div>
                        <div><font class="facturae"><b>Cadena original :</b></font>
                        <p class="cadena_cfd">${split_string( o.cadena_original or '') or '' |entity}</p></div>
                    </td>
                </tr>
            </table>
        %endif
        %if o.invoice_sequence_id.approval_id.type == 'cfdi32':
            <table frame="box" rules="all" width="100%">
                <tr>
                    <td width="17%" valign="top" align="center">
                        ${helper.embed_image('jpeg',str(o.company_emitter_id.cif_file), 140, 220)}
                    </td>
                    <td valign="top" align="left" width="63%">
                        <div><font class="facturae"><b>Sello Digital Emisor:</b></font>
                        <p class="cadena">${split_string( o.sello ) or ''|entity}</p></div>
                        <div><font class="facturae"><b>Sello Digital SAT:</b></font>
                        <p class="cadena">${split_string( o.cfdi_sello or '') or ''|entity}</p></div>
                        <font class="facturae"><b>Cadena original:</b></font>
                        <br/><p class="cadena">${split_string(o.cfdi_cadena_original) or ''|entity}</p>
                    </td>
                    <td width="20%" valign="top" align="center">
                        ${helper.embed_image('jpeg',str(o.cfdi_cbb), 180, 180)}
                    </td>
                </tr>
            </table>
        %endif
    %endfor
</body>
</html>
