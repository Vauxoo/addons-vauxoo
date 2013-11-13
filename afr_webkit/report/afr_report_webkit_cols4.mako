<!DOCTYPE html SYSTEM                                                                                                                            
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<style type="text/css">                                                                         
    ${css}
</style>
</head>

<body style="border:0; margin: 0;" onload="subst()" >
    
    
<!--
        <h1><center>Initial | Debit | Credit | YTD</center></h1> 
-->
 %for obj in objects:
    <table>
        <tr>
            <td width="30%">
                <div>${helper.embed_image('jpeg',str(obj.company_id.logo),250, 120)}</div>
            </td>
            <td width="70%">
                <table style="width: 100%; text-align:center;">
                    <tr><td><div class="td_company_title">${obj.company_id.name or ''|entity}</div></td></tr>
                    <tr><td><div class="td_company">${obj.get_parser_method('get_vat_by_country',data['form']) or ''|entity}</div></td></tr>
                    <tr><td><div class="td_company">${obj.get_parser_method('get_informe_text',data['form']) or ''| entity}</div></td></tr>
                    <tr><td><div class="td_company_date"> ${data['form'] and obj.get_parser_method('get_month',data['form']) or ''}</div></td></tr>
                </table>
            </td>
            <td>
            </td>
        </tr>
    </table> 
    <table width="100%">
         <thead>
            <tr>
                <td class="celdaTituloTabla" style="width: 100%; text-align:left;">${_('Expressed in: %s') % (obj.get_parser_method('exchange_name',data['form'])) or ''|entity}</td>
            </tr>
        </thead>
    </table>
    <table width="100%">
        <tbody>
            <tr>
                <td class="celdaTituloTabla" style="text-align:right;" width="10%">${_('CODE')}</td>
                <td class="celdaTituloTabla" width="42%">${_('ACCOUNT')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="12%">${_('INICIAL')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="12%">${_('DEBIT')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="12%">${_('CREDIT')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="12%">${_('BALANCE')}</td>
            </tr>
            %for line in obj.get_parser_method('lines',data['form']):
                %if line['type'] != 'view':
                    <tr>
                        <i><td class="celdaLineData" style="text-align:right;font-style:italic;" width="10%">${line['label'] == True and line['code'] or ''}</td></i>
                        <td class="celdaLineDataName" width="42%">${line['name'].upper() or line['name'].title() or ''}</td>
                        <td class="celdaLineData" width="12%">${(line['total']==True) and formatLang(line['balanceinit'] and line['balanceinit'] * line.get('change_sign',1.0) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineData" width="12%">${(line['total']==True) and formatLang(line['debit'], digits=2, grouping=True) or ''}</td>
                        <td class="celdaLineData" width="12%">${(line['total']==True) and formatLang(line['credit'], digits=2, grouping=True) or ''}</td>
                        <td class="celdaLineData" width="12%">${(line['total']==True) and formatLang(line['balance'] and line['balance'] * line.get('change_sign',1.0) or 0.0, digits=2, grouping=True) or ''}</td>
                    </tr>
                %elif line['total'] and not line['label']:
                    <tr>
                        <i><td class="celdaLineDataTotal" style="text-align:right;font-style:italic;" width="10%">${line['label'] == True and line['code'] or ''}</td></i>
                        <td class="celdaLineDataTotal" style="text-align:right;" width="42%">${line['name'].upper() or line['name'].title() or ''}</td>
                        <td class="celdaLineDataTotal" width="12%">${(line['total']==True) and formatLang(line['balanceinit'] and line['balanceinit'] * line.get('change_sign',1.0) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineDataTotal" width="12%">${(line['total']==True) and formatLang(line['debit'], digits=2, grouping=True) or ''}</td>
                        <td class="celdaLineDataTotal" width="12%">${(line['total']==True) and formatLang(line['credit'], digits=2, grouping=True) or ''}</td>
                        <td class="celdaLineDataTotal" width="12%">${(line['total']==True) and formatLang(line['balance'] and line['balance'] * line.get('change_sign',1.0) or 0.0, digits=2, grouping=True) or ''}</td>
                    </tr>
                %else:
                    <tr>
                        <td class="celdaLineDataView" style="text-align:right;font-style:italic;" width="10%">${line['label'] == True and line['code'] or ''}</td>
                        <td class="celdaLineDataNameView" width="42%">${line['name'].upper() or line['name'].title() or ''}</td>
                        <td class="celdaLineDataView" width="12%">${(line['total']==True) and formatLang(line['balanceinit'] and line['balanceinit'] * line.get('change_sign',1.0) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineDataView" width="12%">${(line['total']==True) and formatLang(line['debit'], digits=2, grouping=True) or ''}</td>
                        <td class="celdaLineDataView" width="12%">${(line['total']==True) and formatLang(line['credit'], digits=2, grouping=True) or ''}</td>
                        <td class="celdaLineDataView" width="12%">${(line['total']==True) and formatLang(line['balance'] and line['balance'] * line.get('change_sign',1.0) or 0.0, digits=2, grouping=True) or ''}</td>
                    </tr>
                %endif
            %endfor
        </tbody>
    </table>

%endfor
</body>
</html>
