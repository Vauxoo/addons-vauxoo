<!DOCTYPE>
<html>
<head>
<style type="text/css">                                                                         
    ${css}
</style>
</head>

<body style="border:0; margin: 0;" onload="subst()" >
    
    
<!--
        <h1><center>4 QTR | YTD</center></h1> 
-->
 %for obj in objects:
    <table width="100%">
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
            <td>
            </td>
        </tr>
    </table>
    <table width="100%">
        <thead>
            <tr>
                <td class="celdaTituloTabla" colspan="7" style="text-align:left;">${_('Expressed in: %s') % (obj.get_parser_method('exchange_name',data['form'])) or ''}</td>
            </tr>
        </thead>
        <tbody> 
            <tr>
                <td class="celdaTituloTabla" style="text-align:right;" width="10%">${_('CODE')}</td>
                <td class="celdaTituloTabla" width="30%">${_('ACCOUNT')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="10%">${_('Q1')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="10%">${_('Q2')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="10%">${_('Q3')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="10%">${_('Q4')}</td>
                <td class="celdaTituloTabla" style="text-align:center;" width="10%">${_('YTD')}</td>
            </tr> 
            %for line in obj.get_parser_method('lines',data['form']):
                    %if line['type'] != 'view':
                        <tr class="prueba">
                            <td class="celdaLineData" style="text-align:right;font-style:italic;">${line['label'] == True and line['code'] or ''}</td>
                            <td class="celdaLineDataName" >${line['name'].upper() or line['name'].title()}</td>
                            <td class="celdaLineData" style="text-align:right;">${(line['total']==True) and formatLang(line['bal1'] and (line['bal1'] * line.get('change_sign',1)) or 0.0, digits=2, grouping=True)  or ''}</td>
                            <td class="celdaLineData" style="text-align:right;">${(line['total']==True) and formatLang(line['bal2'] and line['bal2'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                            <td class="celdaLineData" style="text-align:right;">${(line['total']==True) and formatLang(line['bal3'] and line['bal3'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                            <td class="celdaLineData" style="text-align:right;">${(line['total']==True) and formatLang(line['bal4'] and line['bal4'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                            <td class="celdaLineData" style="text-align:right;">${(line['total']==True) and formatLang(line['bal5'] and line['bal5'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        </tr>
                    %elif line['total'] and not line['label']:
                        <tr class="prueba">
                            <td class="celdaLineDataTotal" style="text-align:right;font-style:italic;">${line['label'] == True and line['code'] or ''}</td>
                            <td class="celdaLineDataTotal" style="text-align:right;">${line['name'].upper() or line['name'].title() or ''}</td>
                            <td class="celdaLineDataTotal">${(line['total']==True) and formatLang(line['bal1'] and (line['bal1'] * line.get('change_sign',1)) or 0.0, digits=2, grouping=True)  or ''}</td>
                            <td class="celdaLineDataTotal">${(line['total']==True) and formatLang(line['bal2'] and line['bal2'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                            <td class="celdaLineDataTotal">${(line['total']==True) and formatLang(line['bal3'] and line['bal3'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                            <td class="celdaLineDataTotal">${(line['total']==True) and formatLang(line['bal4'] and line['bal4'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                            <td class="celdaLineDataTotal">${(line['total']==True) and formatLang(line['bal5'] and line['bal5'] * line.get('change_sign',1) or 0.0, digits=2, grouping=True)  or ''}</td>
                        </tr>
                    %else:
                        <tr class="prueba">
                            <i><td class="celdaLineDataView" style="text-align:right;font-style:italic;" width="10%">${line['label'] == True and line['code'] or ''}</td></i>
                            <td class="celdaLineDataNameView" colspan="6" >${line['name'].upper() or line['name'].title() or ''}</td>
                        </tr>
                    %endif
            %endfor
        </tbody> 
    </table>
%endfor
</body>
</html>
