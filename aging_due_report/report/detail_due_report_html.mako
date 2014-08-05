<!DOCTYPE>
<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    <% setLang(user.lang) %>
    <table class="basic_table" width="100%">
        <tr>
            <td width="30%">
                <div  style="float:left;">
                    ${helper.embed_image('jpeg',str(company.logo),180, auto)}
                </div>
            </td>
            <td style="text-align: right;">
                <strong>${_('Customer Detail Report of Debts') |entity}</strong>
            </td>
       </tr>
    </table>
    </br>
    <% cur_group = get_invoice_by_partner(objects) %>
    <% print cur_group %>
    %for o in cur_group:
        <table class="table_column_border table_alter_color_row table_title_bg_color" width="100%">
            <tr style=" border-top: 1px solid #000000;">
                <td class="ITEMSLEFT" style="background-color: lightgrey;">${ (o.get('rp_brw').vat and '%s-%s-%s'%( o.get('rp_brw').vat [2], o.get('rp_brw').vat[3:-1], o.get('rp_brw').vat[-1]) or '').upper() }</td>
                <td colspan="5" class="ITEMSLEFT" style="background-color: lightgrey;">${ o.get('rp_brw').name or ''} ${o.get('cur_brw').name or ''}</td>
                <td colspan="4" class="ITEMSLEFT" style="background-color: lightgrey;">${ o.get('rp_brw').ref or ''}</td>
                <td class="ITEMSLEFT" style="background-color: lightgrey;">${ o.get('rp_brw').user_id.name or '' }</td>
                <td colspan="2" class="ITEMSLEFT" style="background-color: lightgrey;">${ 'Amounts expressed in {}'.format(o.get('cur_brw').name) }</td>
            </tr>
            <tr>
                <th width="14%" class="ITEMSTITLELEFT">${_('INVOICE') |entity}</th>
                <th width="8%" class="ITEMSTITLELEFT">${_('EMIS DATE') |entity}</th>
                <th width="8%" class="ITEMSTITLELEFT">${_('DUE DATE') |entity}</th>
                <th width="7%" class="ITEMSTITLELEFT">${_('DUE DAYS') |entity}</th>
                <th width="7%" class="ITEMSTITLERIGHT">${_('BASE') |entity}</th>
                <th width="7%" class="ITEMSTITLERIGHT">${_('TAX') |entity}</th>
                <th width="7%" class="ITEMSTITLERIGHT">${_('TOT/INV.') |entity}</th>
                <th width="7%" class="ITEMSTITLERIGHT">${_('VAT WH') |entity}</th>
                <th width="7%" class="ITEMSTITLERIGHT">${_('INCOME WH') |entity}</th>
                <th width="7%" class="ITEMSTITLERIGHT">${_('MUNI. WH') |entity}</th>
                <th width="7%" class="ITEMSTITLERIGHT">${_('C/N') |entity}</th>
                <th width="7%" class="ITEMSTITLERIGHT">${_('COLLECTS') |entity}</th>
                <th width="7%" class="ITEMSTITLERIGHT">${_('BALANCE') |entity}</th>
            </tr>
        </table>
        </br>
    </br>
    %endfor
    <p style="word-wrap:break-word;"></p>

    </br>
    <p style="page-break-before: always;"></p>

</body>
</html>
