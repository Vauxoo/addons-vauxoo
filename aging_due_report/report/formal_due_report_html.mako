<!DOCTYPE>
<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    <% setLang(user.lang) %>
    %for o in objects:
    <table class="basic_table" width="100%">
        <tr>
            <td width="30%">
                <div  style="float:left;">
                    ${helper.embed_image('jpeg',str(o.company_id.logo),180, auto)}
                </div>
            </td>
       </tr>
    </table>
    </br>
    <% datas = get_invoice_by_partner_group(objects, inv_type='out_invoice') %>
    <% print datas %>
    %for data in datas:
    <div class="ITEMSLEFT"> ${data[0].get('rp_brw').name} </div>
    
    ${ (data[0].get('rp_brw').vat and '%s-%s-%s'%( data[0].get('rp_brw').vat [2], data[0].get('rp_brw').vat[3:-1], data[0].get('rp_brw').vat[-1])).upper() }
    ${data[0].get('rp_brw').street and data[0].get('rp_brw').street.title()}
    ${data[0].get('rp_brw').street2 and data[0].get('rp_brw').street2.title()}
    ${data[0].get('rp_brw').state_id and data[0].get('rp_brw').state_id.name.title()}
    DOCUMENT: Customer Financial Statement
    DATE: ${formatLang(time.strftime('%Y-%m-%d'),date=True)}
   ${company.overdue_msg}
   </br>
        %for line in data:
        <table class="table_column_border table_alter_color_row table_title_bg_color" width="100%">
            <tr>
                <th width="12%" class="ITEMSTITLELEFT">${_('DOCUMENT') |entity}</th>
                <th width="18%" class="ITEMSTITLELEFT">${_('EMIS DATE') |entity}</th>
                <th width="10%" class="ITEMSTITLELEFT">${_('DUE DATE') |entity}</th>
                <th width="10%" class="ITEMSTITLELEFT">${_('DUE DAYS') |entity}</th>
                <th width="10%" class="ITEMSTITLERIGHT">${_('BASE') |entity}</th>
                <th width="10%" class="ITEMSTITLERIGHT">${_('TAX') |entity}</th>
                <th width="10%" class="ITEMSTITLERIGHT">${_('TOTAL/DOC.') |entity}</th>
                <th width="10%" class="ITEMSTITLERIGHT">${_('COLLECTS') |entity}</th>
                <th width="10%" class="ITEMSTITLERIGHT">${_('BALANCE') |entity}</th>
            </tr>
        </table>
        </br>
        %endfor
        %endfor
</br>
    <p style="word-wrap:break-word;"></p>

    </br>
    <p style="page-break-before: always;"></p>

    %endfor

</body>
</html>
