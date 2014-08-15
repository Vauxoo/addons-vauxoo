<!DOCTYPE>
<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    <% setLang(user.lang) %>
    <% datas = get_invoice_by_partner_group(objects, inv_type='in_invoice') %>
    %for data in datas:
    <table class="basic_table" width="100%">
        <tr>
            <td width="30%">
                <div  style="float:left;">
                    ${helper.embed_image('jpeg',str(company.logo),180, auto)}
                </div>
            </td>
            <td style="text-align: center;">
                <strong>${_('Supplier Formal Report of Debts') |entity}</strong>
            </td>
            <td class="CUSTOMERNAME style="text-align: right;">
                ${ formatLang(time.strftime('%Y-%m-%d'), date=True)}
            </td>
       </tr>
    </table>
    
    <em>
        <div class="CUSTOMERNAME">${data[0].get('rp_brw').name}</div>
        <div class="CUSTOMEROTHER">${ (data[0].get('rp_brw').vat and '%s-%s-%s'%( data[0].get('rp_brw').vat [2], data[0].get('rp_brw').vat[3:-1], data[0].get('rp_brw').vat[-1]) or '').upper() }</div>
        <div class="CUSTOMEROTHER">${data[0].get('rp_brw').street and data[0].get('rp_brw').street.title() or ''}</div>
        <div class="CUSTOMEROTHER">${data[0].get('rp_brw').street2 and data[0].get('rp_brw').street2.title() or ''}</div>
        <div class="CUSTOMEROTHER">${data[0].get('rp_brw').state_id and data[0].get('rp_brw').state_id.name.title() or ''}</div>
        </br>
        <div><pre class="CUSTOMERTEXT">${_('Supplier Financial Statement')}</pre></div>
        <div><pre class="CUSTOMERTEXT">${company.overdue_msg}</pre></div>
    </em>
    </br>
        <!-- TABLA DE CABECERA -->
        %for line in data:
            <table class="table_column_border table_alter_color_row table_title_bg_color" width="100%">
                <tr>
                    <th width="15%" class="ITEMSTITLELEFT">${_('DOCUMENT') |entity}</th>
                    <th width="15%" class="ITEMSTITLELEFT">${_('EMIS DATE') |entity}</th>
                    <th width="10%" class="ITEMSTITLELEFT">${_('DUE DATE') |entity}</th>
                    <th width="10%" class="ITEMSTITLELEFT">${_('DUE DAYS') |entity}</th>
                    <th width="10%" class="ITEMSTITLERIGHT">${_('BASE') |entity}</th>
                    <th width="10%" class="ITEMSTITLERIGHT">${_('TAX') |entity}</th>
                    <th width="10%" class="ITEMSTITLERIGHT">${_('TOTAL/DOC.') |entity}</th>
                    <th width="10%" class="ITEMSTITLERIGHT">${_('PAYMENTS') |entity}</th>
                    <th width="10%" class="ITEMSTITLERIGHT">${_('BALANCE') |entity}</th>
                </tr>

                <!-- TABLA CENTRAL DEL REPORTE -->
                %for inv in line['inv_ids']:
                    <tr>
                        <td class="ITEMSLEFT">${_('I:')} ${inv['inv_brw'].number or 0}</td>
                        <td class="ITEMSLEFT">${ formatLang(inv['inv_brw'].date_invoice, date=True) }</td>
                        <td class="ITEMSLEFT">${ formatLang(inv['inv_brw'].date_due, date=True) }</td>
                        <td class="ITEMSLEFT">${ inv.get('due_days') and '%s DAYS'%inv.get('due_days') or _('0 DAYS') }</td>
                        <td class="ITEMSRIGHT">${ formatLang(inv['inv_brw'].amount_untaxed) or '0.00' }</td>
                        <td class="ITEMSRIGHT">${ formatLang(inv['inv_brw'].amount_tax) or '0.00' }</td>
                        <td class="ITEMSRIGHT">${ formatLang(inv['inv_brw'].amount_total) or '0.00' }</td>
                        <td class="ITEMSRIGHT">${ formatLang(inv.get('payment')) or '0.00' }</td>
                        <td class="ITEMSRIGHT">${ formatLang(inv.get('residual')) or '0.00' }</td>
                    </tr>
                    <!-- TABLE DE REFUNDS -->
                        %for ref_brw in inv['refund_brws']:
                        <tr>
                            <td class="ITEMSLEFT">${_('C:')} ${int(ref_brw.number or 0)}</td>
                            <td class="ITEMSLEFT">${ formatLang(ref_brw.date_invoice,date=True) }</td>
                            <td class="ITEMSLEFT"></td>
                            <td class="ITEMSLEFT"></td>
                            <td class="ITEMSRIGHT">${ formatLang(ref_brw.amount_untaxed) or '0.00' }</td>
                            <td class="ITEMSRIGHT">${ formatLang(ref_brw.amount_tax) or '0.00' }</td>
                            <td class="ITEMSRIGHT">${ formatLang(ref_brw.amount_total) or '0.00'}</td>
                            <td class="ITEMSRIGHT"></td>
                            <td class="ITEMSRIGHT"></td>
                        </tr>
                        %endfor
                %endfor
                <tr style=" border-top: 1px solid #000000;">
                    <td class="ITEMSLEFT" style="background-color: lightgrey;">${_('I: INVOICE')}</td>
                    <td class="ITEMSLEFT" style="background-color: lightgrey;">${_('C: C/N')}</td>
                    <td class="ITEMSLEFT" style="background-color: lightgrey;">${_('D: D/N')}</td>
                    <td class="ITEMSRIGHT" colspan="3" style="background-color: lightgrey;">${_('TOTAL IN ')} ${line.get('cur_brw').name}</td>
                    <td class="ITEMSRIGHT" style="background-color: lightgrey;">${formatLang(line.get('inv_total')) or '0.00'}</td>
                    <td class="ITEMSRIGHT" style="background-color: lightgrey;">${formatLang(line.get('pay_total')) or '0.00'}</td>
                    <td class="ITEMSRIGHT" style="background-color: lightgrey;">${formatLang(line.get('due_total')) or '0.00'}</td>
                </tr>
            </table>
            </br>
        %endfor
        

    </br>
    <em>
    <div class="CUSTOMERTEXT">${_('Without any further reference,')}</div>
    </br>
    <div class="CUSTOMERCENTER">${_('Best Regards,')}</div>
    </br>
    <div class="CUSTOMERCENTER">${ user.signature }</div>
    </em>
    <p style="word-wrap:break-word;"></p>

    </br>
    <p style="page-break-before: always;"></p>
    %endfor
</body>
</html>
