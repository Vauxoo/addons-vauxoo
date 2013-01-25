<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    %for o in objects :
        <div class="title">${o.company_emitter_id.address_invoice_parent_company_id.name or ''|entity}</div>
        <table>
            <tr>
                <td width=220>
                    ${helper.embed_image('jpeg',str(o.company_emitter_id.logo),200, 150)}
                </td>
                <td class="td_data_exp">
                    <div class="emitter">Calle: ${o.company_emitter_id.address_invoice_parent_company_id.street or ''|entity}
                    Nro. Ext: ${o.company_emitter_id.address_invoice_parent_company_id.street3 or ''|entity}
                    Int: ${o.company_emitter_id.address_invoice_parent_company_id.street4 or ''|entity}
                    <br />Colonia: ${o.company_emitter_id.address_invoice_parent_company_id.street2 or ''|entity}
                    <br />Ciudad: ${o.company_emitter_id.address_invoice_parent_company_id.city or ''|entity} 
                    Estado: ${o.company_emitter_id.address_invoice_parent_company_id.state_id and o.company_emitter_id.address_invoice_parent_company_id.state_id.name or ''|entity}
                    <br />Localidad: ${ o.company_emitter_id.address_invoice_parent_company_id.city2 or ''|entity}
                    <br />CP: ${ o.company_emitter_id.address_invoice_parent_company_id.zip or ''|entity}
                    <br/>RFC: ${ o.company_emitter_id.partner_id._columns.has_key('vat_split') and o.company_emitter_id.partner_id.vat_split or o.company_emitter_id.partner_id.vat|entity}
                    <br/>Teléfono(s):
                    <br/>
                    ${o.company_emitter_id.address_invoice_parent_company_id.phone or ''|entity}
                    ${o.company_emitter_id.address_invoice_parent_company_id.fax or ''|entity}
                    ${o.company_emitter_id.address_invoice_parent_company_id.mobile or ''|entity}</div>
                </td>
                <td width=250>
                    <div class="folio">Folio:
                    <%number = 'SIN FOLIO O ESTATUS NO VALIDO'%>
                    <%  if o.type in ['out_invoice', 'out_refund']:
                            if o.state in ['open', 'paid', 'cancel']:
                                number=o.number%>
                        ${number or ''|entity}</div>
                    %if o.state == 'cancel': 
                        ${'FACTURA CANCELADA' |entity} 
                    %endif
                    %if o.address_issued_id:
                        ${o.address_issued_id.city or ''|entity}
                        %if o.address_issued_id.state_id:
                            , ${o.address_issued_id.state_id.name or ''|entity}
                        %endif
                    %endif
                    <br/>a ${o.date_invoice_tz or ''|entity}
                    <br/>Serie: Falta
                    <br/>Aprobación: Falta
                    <br/>Año Aprobación: Falta
                </td>
            </tr>
        </table>
        <table class="line" width="100%" border="1"></table>
        <table>
            <tr>
                <td class="address">
                    <font color="#280099">Receptor</font>
                    <br/>Nombre: ${o.partner_id.name or ''|entity}
                    <br/>Dirección: ${get_data_partner(o.partner_id)['street'] or ''|entity} No. Ext: ${get_data_partner(o.partner_id)['street3'] or ''|entity} Int: ${get_data_partner(o.partner_id)['street4'] or ''|entity}
                    <br/>Colonia: ${get_data_partner(o.partner_id)['street2'] or ''|entity}
                    <br/>Localidad: ${get_data_partner(o.partner_id)['city2'] or ''|entity}
                    <br/>C.P.: ${get_data_partner(o.partner_id)['zip'] or ''|entity}
                    <br/>R. F. C. : ${get_data_partner(o.partner_id)['vat'] or ''|entity}
                </td>
            </tr>
        </table>
        <table>
            <tr>
                <td width=80>Cant.</td>
                <td width=80>Unidad</td>
                <td width=220>Descripción</td>
                <td width=80>Clave</td>
                <td width=80>P.Unitario</td>
                <td width=80>Dto. %</td>
                <td width=80>Importe</td>
            </tr>
            %for l in o.invoice_line: 
                <tr>
                    <td width=80>${l.quantity}</td>
                    <td width=80>${l.uos_id.name or ''|entity}</td>
                    <td width=220>${l.name or ''|entity}</td>
                    <td width=80>${l.product_id.default_code or ''|entity}</td>
                    <td width=80>${formatLang(l.price_unit) or ''|entity}</td>
                    <td width=80>${formatLang(l.discount) or ''|entity} %</td>
                    <td width=80>$Falta Importe</td>
                </tr>
            %endfor
        </table>
        <table align="right">
            <tr>
                <td>Suma $</td>
                <td>${o.amount_untaxed or 0.0 |entity}</td>
            </tr>
            <tr>
                <td>Descuento:</td>
                <td>${o.amount_untaxed or 0.0 |entity}</td>
            </tr>
            <tr>
                <td>Sub Total $</td>
                <td>${formatLang(o.amount_untaxed) or ''|entity}</td>
            </tr>
        </table>
    %endfor
</body>
</html>
