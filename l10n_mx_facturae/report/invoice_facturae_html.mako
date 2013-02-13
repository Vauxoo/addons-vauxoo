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
                                ${o.company_emitter_id.address_invoice_parent_company_id.street3 or ''|entity}
                                ${o.company_emitter_id.address_invoice_parent_company_id.street4 or ''|entity}
                                ${o.company_emitter_id.address_invoice_parent_company_id.street2 or ''|entity}
                                ${ o.company_emitter_id.address_invoice_parent_company_id.zip or ''|entity}
                                <br />${_("Localidad:")} ${ o.company_emitter_id.address_invoice_parent_company_id.city2 or ''|entity}
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
                            <font class="font">Condición de pago:
                            <font class="font">${o.payment_term.note or o.payment_term.name or ''|entity}</font>
                        %endif
                        <br/><font class="font">Expedido en:</font>
                        %if o.address_issued_id:
                            <br/><font class="font">${o.address_issued_id.name or ''|entity}</font>
                            <br/><font class="font">${o.address_issued_id.street or ''|entity}</font>
                            <font class="font">${o.address_issued_id.street3 or ''|entity}</font>
                            <font class="font">${o.address_issued_id.street4 or ''|entity}</font>
                            <br/><font class="font">${o.address_issued_id.street2 or ''|entity}</font>
                            <font class="font">${o.address_issued_id.zip or ''|entity}</font>
                            <br/><font class="font">Localidad: ${o.address_issued_id.city2 or ''|entity}</font>
                            <br/><font class="font">${o.address_issued_id.city or ''|entity}</font>
                            <font class="font">${o.address_issued_id.state_id.name and ',' or ''|entity} ${o.address_issued_id.state_id and o.address_issued_id.state_id.name or ''|entity}</font>
                            <font class="font">${o.address_issued_id.country_id.name and ',' or ''|entity} ${o.address_issued_id.country_id and o.address_issued_id.country_id.name or ''|entity}</font>
                        %endif
                    <div/>
                </td>
            </tr>
        </table>
        <table class="line" width="100%" border="1"></table>
        <font size="15"></font>
        <table>
            <tr>
                <td class="address" width="1100">
                    <div>
                        <table class="table_cliente">
                            <tr>
                                <td width="10%" class="cliente"><font class="font"><b>Receptor:</b></font></td>
                                <td width="58%" class="cliente"><font class="font">${o.partner_id.name or ''|entity}</font></td>
                                <td width="9%" class="cliente"><font class="font"><b>R. F. C.:</b></font></td>
                                <td width="23%" class="cliente"><font class="font"><b>${get_data_partner(o.partner_id) and get_data_partner(o.partner_id)['vat'] or ''|entity}</b></font></td>
                            </tr>
                        </table>
                    <div>
                    </div>
                        <table class="table_cliente" style="border-collapse:collapse">
                            <tr>
                                <td width="10%" class="cliente"><font class="font"><b>Calle:</b></font></td>
                                <td width="58%" class="cliente"><font class="font">${get_data_partner(o.partner_id) and get_data_partner(o.partner_id)['street'] or ''|entity}</font></td>
                                %if get_data_partner(o.partner_id) and get_data_partner(o.partner_id)['street3']:
                                    <td width="9%" class="cliente"><font class="font"><b>No. Ext:</b></font></td>
                                    <td width="8%" class="cliente"><font class="font">${get_data_partner(o.partner_id) and get_data_partner(o.partner_id)['street3'] or ''|entity}</font></td>
                                %endif
                                %if get_data_partner(o.partner_id) and get_data_partner(o.partner_id)['street4']:
                                    <td width="7%" class="cliente"><font class="font"><b>Int:</b></font></td>
                                    <td width="8%" class="cliente"><font class="font">${get_data_partner(o.partner_id) and get_data_partner(o.partner_id)['street4'] or ''|entity}</font></td>
                                %endif
                            </tr>
                        </table>
                    </div>
                    <div>
                        <table class="table_cliente">
                            <tr>
                                <td width="10%" class="cliente"><font class="font"><b>Colonia:</b></font></td>
                                <td width="30%" class="cliente"><font class="font">${get_data_partner(o.partner_id) and get_data_partner(o.partner_id)['street2'] or ''|entity}</font></td>
                                <td width="10%" class="cliente"><font class="font"><b>C.P.:</b></font></td>
                                <td width="18%" class="cliente"><font class="font">${get_data_partner(o.partner_id) and get_data_partner(o.partner_id)['zip'] or ''|entity}</font></td>
                                <td width="9%" class="cliente"><font class="font"><b>Localidad:</b></font></td>
                                <td width="23%" class="cliente"><font class="font">${get_data_partner(o.partner_id) and get_data_partner(o.partner_id)['city2'] or ''|entity}</font></td>
                            </tr>
                        </table>
                    </div>
                    <div>
                        <table class="table_cliente">
                            <tr>
                                <td width="10%" class="cliente"><font class="font"><b>Ciudad:</b></font></td>
                                <td width="30%" class="cliente"><font class="font">${get_data_partner(o.partner_id) and get_data_partner(o.partner_id)['city'] or ''|entity}</font></td>
                                <td width="10%" class="cliente"><font class="font"><b>Estado:</b></font></td>
                                <td width="18%" class="cliente"><font class="font">${get_data_partner(o.partner_id) and get_data_partner(o.partner_id)['state'] or ''|entity}</font></td>
                                <td width="9%" class="cliente"><font class="font"><b>Pais:</b></font></td>
                                <td width="23%" class="cliente"><font class="font">${get_data_partner(o.partner_id) and get_data_partner(o.partner_id)['country'] or ''|entity}</font></td>
                            </tr>
                        </table>
                    </div>
                    <div>
                        <table class="table_cliente">
                            <tr>
                                <td width="10%" class="cliente"><font class="font"><b>Telefono(s):</b></font></td>
                                <td width="58%" class="cliente"><font class="font">
                                   ${get_data_partner(o.partner_id) and get_data_partner(o.partner_id)['phone'] or ''|entity}
                                   ${get_data_partner(o.partner_id) and get_data_partner(o.partner_id)['fax'] and ',' or ''|entity} ${get_data_partner(o.partner_id) and get_data_partner(o.partner_id)['fax'] or ''|entity}
                                   ${get_data_partner(o.partner_id) and get_data_partner(o.partner_id)['mobile'] and ',' or ''|entity} ${get_data_partner(o.partner_id) and get_data_partner(o.partner_id)['mobile'] or ''|entity}</font>
                                <td width="9%" class="cliente"><font class="font"><b>Origen:</b></font></td>
                                <td width="23%" class="cliente"><font class="font"><b>${o.origin or ''|entity}</b></font></td>
                            </tr>
                        </table>
                    </div>
                </td>
                <td width="10"></td>
                <td width="10"></td>
                <td width="280" align="center">
                    %if o.address_issued_id:
                        <font class="font">${o.address_issued_id.city or ''|entity}<font/>
                        , <font class="font">${o.address_issued_id.state_id and o.address_issued_id.state_id.name or ''|entity}</font>
                        , <font class="font">${o.address_issued_id.country_id and o.address_issued_id.country_id.name or ''|entity}</font>
                    %endif
                    <br/><font class="font">${"a"} ${o.date_invoice_tz or ''|entity}</font>
                    %if o.invoice_sequence_id.approval_id.type != 'cbb':
                    <div><font class="font">${_("Serie:")} ${get_approval() and get_approval().serie or ''|entity}
                    <br/>${_("Aprobación:")} ${get_approval() and get_approval().approval_number or ''|entity}
                    <br/>${_("Año Aprobación:")} ${get_approval() and get_approval().approval_year or ''|entity}<font/></div>
                    %endif
                </td>
            </tr>
        </table>
        <br/>
        <table style="border-collapse:collapse" width="100%">
            <tr>
                <td width="10%" class="label_lines"><b><font class="lines_font">${_("Cant.")}</font></b></td>
                <td width="1%" class="label_lines"></td>
                <td width="10%" class="label_lines"><b><font class="lines_font">${_("Unidad")}</font></b></td>
                <td width="47%" class="label_lines"><b><font class="lines_font">${_("Descripción")}</font></b></td>
                <td width="9%" class="label_lines" align="right"><b><font class="lines_font">${_("P.Unitario")}</font></b></td>
                <td width="8%" class="label_lines" align="right"><b><font class="lines_font">${has_disc(o.invoice_line) == 'True' and _("Dto. %") or ''}</font></b></td>
                <td width="15%" class="label_lines" align="right"><b><font class="lines_font">${_("Importe")}</font></b></td>
            </tr>
            %for l in o.invoice_line: 
                <tr>
                    <td width="10%" class="label_data" align="right"><font class="lines">${l.quantity or '0.0'}</font></td>
                    <td width="1%" class="label_data"></td>
                    <td width="10%" class="label_data"><font class="lines">${l.uos_id.name or ''|entity}</font></td>
                    <td width="47%" class="label_data"><font class="lines">${l.name or ''|entity}</font></td>
                    <td width="9%" class="label_data" align="right"><font class="lines">${formatLang(l.price_unit) or '0.0'|entity}</font></td>
                    <td width="8%" class="label_data" align="right"><font class="lines">${has_disc(o.invoice_line) == 'True' and formatLang(l.discount) or ''|entity} ${has_disc(o.invoice_line) == 'True' and '%' or ''|entity}</font></td>
                    <td width="15%" class="label_data" align="right"><font class="lines">${formatLang(l.price_subtotal) or '0.0'|entity}</font></td>
                </tr>
            %endfor
        </table>
        <table align="right" width="100%" style="border-collapse:collapse">
            %if get_taxes() or get_taxes_ret():
                <tr>
                    <td width="70%"></td>
                    <td width="15%" class="total_line"><font class="lines">${_("Sub Total:")} $</font></td>
                    <td width="15%" align="right" class="total_line"><font class="lines">${formatLang(o.amount_untaxed) or ''|entity}</font></td>
                </tr>
            %endif
            %for tax in get_taxes(): 
                <tr>
                    <td width="70%"></td>
                    <td width="15%"><font class="lines">${tax['name2']} ${round(float(tax['tax_percent']))} ${"% $"}</font></td>
                    <td width="15%" align="right"><font class="lines">${formatLang(float( tax['amount'] ) ) or ''|entity}</font></td>
                </tr>
            %endfor
            %for tax_ret in get_taxes_ret():
                <tr>
                    <td width="70%"></td>
                    <td width="15%"><font class="lines">${tax_ret['name2']} ${"Ret"} ${round( float( tax_ret['tax_percent'] ), 2 )*-1 } ${"% $"}</font></td>
                    <td width="15%" align="right"><font class="lines">${formatLang( float( tax_ret['amount'] )*-1 ) or ''|entity}</font></td>
                </tr>
            %endfor
            <tr align="left">
                <td width="70%"></td>
                <td width="15%" class="total_line"><font class="lines"><b>${_("Total:")} $</b></font></td>
                <td width="15%" class="total_line" align="right"><font class="lines"><b>${formatLang(o.amount_total) or ''|entity}</b></font></td>
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
            <div style="page-break-before:always;">
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
            </div>
        %endif
    %endfor
</body>
</html>
