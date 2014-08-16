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
            <td style="text-align: center;">
                <strong>${_('Customer Detail Report of Debts') |entity}</strong>
            </td>
            <td class="CUSTOMERNAME style="text-align: right;">${ formatLang(time.strftime('%Y-%m-%d'), date=True)}</td>
       </tr>
    </table>
    </br>
    <% cur_group = get_invoice_by_partner(objects) %>
    %for o in cur_group:
        <table class="table_column_border table_alter_color_row table_title_bg_color" width="100%">
            <tr style="border-top: 1px solid #000000;">
                <td class="ITEMSLEFT" style="background-color: lightgrey; font-size: 10;">${ (o.get('rp_brw').vat and '%s-%s-%s'%( o.get('rp_brw').vat [2], o.get('rp_brw').vat[3:-1], o.get('rp_brw').vat[-1]) or '').upper() }</td>
                <td colspan="5" class="ITEMSLEFT" style="background-color: lightgrey; font-size: 10;">${ o.get('rp_brw').name or ''} (${ o.get('cur_brw').name or '' })</td>
                <td colspan="1" class="ITEMSLEFT" style="background-color: lightgrey; font-size: 10;">${ o.get('rp_brw').ref or ''} ({ o.get('rp_brw').user_id.name or '' })</td>
                <td colspan="2" class="ITEMSLEFT" style="background-color: lightgrey; font-size: 10;">${ _('Amounts expressed in') + ' ('+o.get('cur_brw').name+')' }</td>
            </tr>
            <tr>
                <th width="14%" class="ITEMSTITLELEFT">${_('INVOICE') |entity}</th>
                <th width="8%" class="ITEMSTITLELEFT">${_('EMIS DATE') |entity}</th>
                <th width="8%" class="ITEMSTITLELEFT">${_('DUE DATE') |entity}</th>
                <th width="7%" class="ITEMSTITLELEFT">${_('DUE DAYS') |entity}</th>
                <th width="7%" class="ITEMSTITLERIGHT">${_('BASE') |entity}</th>
                <th width="7%" class="ITEMSTITLERIGHT">${_('TAX') |entity}</th>
                <th width="7%" class="ITEMSTITLERIGHT">${_('TOT/INV.') |entity}</th>
                <th width="7%" class="ITEMSTITLERIGHT">${_('COLLECTS') |entity}</th>
                <th width="7%" class="ITEMSTITLERIGHT">${_('BALANCE') |entity}</th>
            </tr>
            %for inv in o['inv_ids']:
                <tr>
                    <td class="ITEMSLEFT">${inv['inv_brw'].number}</td>
                    <td class="ITEMSLEFT">${ formatLang(inv['inv_brw'].date_invoice,date=True)}</td>
                    <td class="ITEMSLEFT">${ formatLang(inv['inv_brw'].date_due,date=True)}</td>
                    <td class="ITEMSLEFT">${ inv.get('due_days') and _('%s DAYS')%inv.get('due_days') or _('0 DAYS') }</td>
                    <td class="ITEMSRIGHT">${formatLang(inv['inv_brw'].amount_untaxed) or '0.00' }</td>
                    <td class="ITEMSRIGHT">${formatLang(inv['inv_brw'].amount_tax) or '0.00'}</td>
                    <td class="ITEMSRIGHT">${formatLang(inv['inv_brw'].amount_total) or '0.00'}</td>
                    <td class="ITEMSRIGHT">${formatLang(inv.get('payment_left')) or '0.00'}</td>
                    <td class="ITEMSRIGHT">${formatLang(inv.get('residual')) or '0.00'}</td>
                </tr>
            %endfor
                <tr>
                    <td class="ITEMSRIGHT ITEMBOLD" colspan="6" style="background-color: lightgrey;font-size: 8;">${ _('TOTAL') }</td>
                    <td class="ITEMSRIGHT ITEMBOLD" style="background-color: lightgrey;font-size: 8;">${ formatLang(o.get('inv_total')) or '0.00' }</td>
                    <td class="ITEMSRIGHT ITEMBOLD" style="background-color: lightgrey;font-size: 8;">${ formatLang(o.get('pay_left_total')) or '0.00'}</td>
                    <td class="ITEMSRIGHT ITEMBOLD" style="background-color: lightgrey;font-size: 8;">${ formatLang(o.get('due_total')) or '0.00'}</td>
                </tr>
        </table>
        </br>
        %endfor
        <% list = get_total_by_comercial(objects) %>
        <table style="border: 1px solid #A41D35; border-collapse: collapse;" width="100%">
            %for p in list:
            <tr>
                <td width="92%" class="ITEMSRIGHT" style="background-color: lightgrey;border: 1px solid #A41D35; font-size: 8;">${_('TOTAL IN')} ${ p['currency']}</td>
                <td width="8%" class="ITEMSRIGHT" style="background-color: lightgrey;border: 1px solid #A41D35; font-size: 8;">${ formatLang(p['total']) or '0.00' }</td>
            </tr>
            %endfor
        </table>
    <p style="word-wrap:break-word;"></p>

    </br>
    <p style="page-break-before: always;"></p>

</body>
</html>
