<!DOCTYPE>
<html>
<head>
<style type="text/css">                                                                         
    ${css}
</style>
</head>

<body style="border:0; margin: 0;" onload="subst()" >

%for obj in objects:
<table>
    <tr>
        <td width="30%">
            <div>${helper.embed_image('jpeg',str(obj.company_id.logo),250, 120)}</div>
        </td>
        <td width="70%">
            <table style="width: 100%; text-align:center;">
                <tr><td><div class="td_company_title">${obj.company_id.name or ''}</div></td></tr>
                <tr><td><div class="td_company">${obj.get_parser_method('get_vat_by_country',data['form']) or ''}</div></td></tr>
                <tr><td><div class="td_company">${obj.get_parser_method('get_informe_text',data['form']) or ''}</div></td></tr>
                <tr><td><div class="td_company_date"> ${data['form'] and obj.get_parser_method('get_month',data['form']) or ''}</div></td></tr>
            </table>
        </td>
    </tr>
</table> 
<table width="100%">
     <thead>
        <tr>
            <td class="celdaTituloTabla" style="width: 100%; text-align:left;">${_('Expressed in: %s') % (obj.get_parser_method('exchange_name',data['form'])) or ''}</td>
        </tr>
    </thead>
</table>
<table style="width: 100%;">
    <tr>
        <td class="celdaTituloTabla" style="text-align:right;" width="10%">${_('Code')}</td>
        <td class="celdaTituloTabla" width="30%">${_('ACCOUNT')}</td>
        <td class="celdaTituloTabla" width="10%">${_('INIT. BAL.')}</td>
        <td class="celdaTituloTabla" style="text-align:center;" width="10%">${_('DEBIT')}</td>
        <td class="celdaTituloTabla" style="text-align:center;" width="10%">${_('CREDIT')}</td>
        <td class="celdaTituloTabla" style="text-align:center;" width="10%">${_('PERIOD')}</td>
        <td class="celdaTituloTabla" style="text-align:center;" width="10%">${_('YTD')}</td>
    </tr> 
    %for line in obj.get_parser_method('lines',data['form']):
            %if line['type'] != 'view':
                <tr>
                    <td class="celdaLineData" style="text-align:right;font-style:italic;">${line['label'] == True and line['code'] or ''}</td>
                    <td class="celdaLineDataName" >${line['name'].upper() or line['name'].title()}</td>
                    <td class="celdaLineData" style="text-align:right;">${(line['total']==True) and formatLang(line.get('change_sign', 1.0) * line.get('balanceinit'), digits=2, grouping=True) or ''}</td>
                    <td class="celdaLineData" style="text-align:right;">${(line['total']==True) and formatLang(line['debit'], digits=2, grouping=True) or ''}</td>
                    <td class="celdaLineData" style="text-align:right;">${(line['total']==True) and formatLang(line['credit'], digits=2, grouping=True) or ''}</td>
                    <td class="celdaLineData" style="text-align:right;">${(line['total']==True) and formatLang(line.get('change_sign', 1.0) * line.get('ytd'), digits=2, grouping=True) or ''}</td>
                    <td class="celdaLineData" style="text-align:right;">${(line['total']==True) and formatLang(line.get('change_sign', 1.0) * line.get('balance'), digits=2, grouping=True) or ''}</td>
                </tr>
            %elif line['total'] and not line['label']:
                <tr>
                    <td class="celdaLineDataTotal" style="text-align:right;font-style:italic;">${line['label'] == True and line['code'] or ''}</td>
                    <td class="celdaLineDataTotal" style="text-align:right;">${line['name'].upper() or line['name'].title() or ''}</td>
                    <td class="celdaLineDataTotal">${(line['total']==True) and formatLang(line.get('change_sign', 1.0) * line.get('balanceinit'), digits=2, grouping=True) or ''}</td>
                    <td class="celdaLineDataTotal">${(line['total']==True) and formatLang(line['debit'], digits=2, grouping=True) or ''}</td>
                    <td class="celdaLineDataTotal">${(line['total']==True) and formatLang(line['credit'], digits=2, grouping=True) or ''}</td>
                    <td class="celdaLineDataTotal">${(line['total']==True) and formatLang(line.get('change_sign', 1.0) * line.get('ytd'), digits=2, grouping=True) or ''}</td>
                    <td class="celdaLineDataTotal">${(line['total']==True) and formatLang(line.get('change_sign', 1.0) * line.get('balance'), digits=2, grouping=True) or ''}</td>
                </tr>
            %else:
                <tr>
                    <td class="celdaLineDataView" style="text-align:right;font-style:italic;" width="10%">${line['label'] == True and line['code'] or ''}</td>
                    <td class="celdaLineDataNameView" colspan="6">${line['name'].upper() or line['name'].title() or ''}</td>
                </tr>
            %endif
    %endfor
</table>
%endfor
</body>
</html>
