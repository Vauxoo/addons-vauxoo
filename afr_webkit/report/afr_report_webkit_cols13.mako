<!DOCTYPE>
<html>
<head>
<style type="text/css">                                                                         
    ${css}
</style>
</head>

<body>
<!--
<h1><center>12 Months | YTD</center></h1> 
-->
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
                <td class="celdaTituloTabla" style="width: 100%; text-align:left;" colspan="15">${_('Expressed in: %s') % (obj.get_parser_method('exchange_name',data['form'])) or ''}</td>
            </tr>
        </thead>
        <tbody>
            <tr class="prueba">
                <td class="celdaTituloTabla" style="text-align:right;" width="6%">${_('CODE')}</td>
                <td class="celdaTituloTabla" width="16%">${_('ACCOUNT')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="6%">${_('01')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="6%">${_('02')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="6%">${_('03')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="6%">${_('04')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="6%">${_('05')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="6%">${_('06')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="6%">${_('07')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="6%">${_('08')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="6%">${_('09')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="6%">${_('10')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="6%">${_('11')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="6%">${_('12')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="6%">${_('YTD')}</td>
            </tr>
            %for line in obj.get_parser_method('lines',data['form']):
                %if line['type'] != 'view':
                    <tr>
                        <td class="celdaLineData" style="text-align:right;font-style:italic;" width="6%">${line['label'] == True and line['code'] or ''}</td>
                        <td class="celdaLineDataName" width="16%">${line['name'].upper() or line['name'].title() or ''}</td>
                        <td class="celdaLineData" width="6%">${(line['total']==True) and formatLang(line['bal1'] and line['bal1'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineData" width="6%">${(line['total']==True) and formatLang(line['bal2'] and line['bal2'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineData" width="6%">${(line['total']==True) and formatLang(line['bal3'] and line['bal3'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineData" width="6%">${(line['total']==True) and formatLang(line['bal4'] and line['bal4'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineData" width="6%">${(line['total']==True) and formatLang(line['bal5'] and line['bal5'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineData" width="6%">${(line['total']==True) and formatLang(line['bal6'] and line['bal6'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineData" width="6%">${(line['total']==True) and formatLang(line['bal7'] and line['bal7'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineData" width="6%">${(line['total']==True) and formatLang(line['bal8'] and line['bal8'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineData" width="6%">${(line['total']==True) and formatLang(line['bal9'] and line['bal9'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineData" width="6%">${(line['total']==True) and formatLang(line['bal10'] and line['bal10'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineData" width="6%">${(line['total']==True) and formatLang(line['bal11'] and line['bal11'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineData" width="6%">${(line['total']==True) and formatLang(line['bal12'] and line['bal12'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineData" width="6%">${(line['total']==True) and formatLang(line['bal13'] and line['bal13'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                    </tr>
                %elif line['total'] and not line['label']:
                    <tr>
                        <td class="celdaLineDataTotal" style="text-align:right;font-style:italic;" width="6%">${line['label'] == True and line['code'] or ''}</td>
                        <td class="celdaLineDataTotal" width="16%">${line['name'].upper() or line['name'].title() or ''}</td>
                        <td class="celdaLineDataTotal" width="6%">${(line['total']==True) and formatLang(line['bal1'] and line['bal1'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineDataTotal" width="6%">${(line['total']==True) and formatLang(line['bal2'] and line['bal2'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineDataTotal" width="6%">${(line['total']==True) and formatLang(line['bal3'] and line['bal3'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineDataTotal" width="6%">${(line['total']==True) and formatLang(line['bal4'] and line['bal4'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineDataTotal" width="6%">${(line['total']==True) and formatLang(line['bal5'] and line['bal5'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineDataTotal" width="6%">${(line['total']==True) and formatLang(line['bal6'] and line['bal6'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineDataTotal" width="6%">${(line['total']==True) and formatLang(line['bal7'] and line['bal7'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineDataTotal" width="6%">${(line['total']==True) and formatLang(line['bal8'] and line['bal8'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineDataTotal" width="6%">${(line['total']==True) and formatLang(line['bal9'] and line['bal9'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineDataTotal" width="6%">${(line['total']==True) and formatLang(line['bal10'] and line['bal10'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineDataTotal" width="6%">${(line['total']==True) and formatLang(line['bal11'] and line['bal11'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineDataTotal" width="6%">${(line['total']==True) and formatLang(line['bal12'] and line['bal12'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineDataTotal" width="6%">${(line['total']==True) and formatLang(line['bal13'] and line['bal13'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                    </tr>
                %else:
                    <tr>
                        <td class="celdaLineDataView" style="text-align:right;font-style:italic;" width="6%">${line['label'] == True and line['code'] or ''}</td>
                        <td class="celdaLineDataNameView" colspan="14">${line['name'].upper() or line['name'].title() or ''}</td>
                    </tr>
                %endif
            %endfor
        </tbody>
    </table>
%endfor
</body>
</html>
