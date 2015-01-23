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
                    <tr><td><div class="td_company">${_(Expressed in data['form'] and (' %s'% obj.get_parser_method('exchange_name',data['form'])) or '')}</div></td></tr>
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
                <td class="celdaTituloTabla" style="width: 100%; text-align:left;">${_('Expressed in: %s') % (obj.get_parser_method('exchange_name',data['form'])) or ''}</td>
            </tr>
        </thead>
    </table>
    <table width="100%">
        <tbody>
             <tr class="prueba">
                <td class="celdaTituloTabla" style="text-align:right;" width="10%">${_('CODE')}</td>
                <td class="celdaTituloTabla" width="70%">${_('ACCOUNT')}</td>
                <center>
                    <td class="celdaTituloTabla" style="text-align:center;"  width="20%">${_('BALANCE')}</td>
                </center>
            </tr>
            %for line in obj.get_parser_method('lines',data['form']):
                %if line['type'] != 'view':
                    <tr class="prueba">
                        <i><td class="celdaLineData" style="text-align:right;font-style:italic;" width="10%">${line['label'] == True and line['code'] or ''}</td></i>
                        <td class="celdaLineDataName" width="70%">${line['name'].upper() or line['name'].title() or ''}</td>
                        <td class="celdaLineData" width="20%">${(line['total']==True) and formatLang(line['balance'] and line['balance'] * line.get('change_sign',1.0) or 0.0, digits=2, grouping=True) or ''}</td>
                    </tr>
                %elif line['total'] and not line['label']:
                    <tr class="prueba">
                        <i><td class="celdaLineDataTotal" style="text-align:right;font-style:italic;" width="10%">${line['label'] == True and line['code'] or ''}</td></i>
                        <td class="celdaLineDataTotal" style="text-align:right;" width="70%">${line['name'].upper() or line['name'].title() or ''}</td>
                        <td class="celdaLineDataTotal" width="20%">${(line['total']==True) and formatLang(line['balance'] and line['balance'] * line.get('change_sign',1.0) or 0.0, digits=2, grouping=True) or ''}</td>
                    </tr>
                %else:
                    <tr class="prueba">
                        <i><td class="celdaLineDataView"  style="text-align:right;font-style:italic;" width="10%">${line['label'] == True and line['code'] or ''}</td></i>
                        <td class="celdaLineDataNameView" width="70%">${line['name'].upper() or line['name'].title() or ''}</td>
                        <td class="celdaLineDataView" width="20%">${(line['total']==True) and formatLang(line['balance'] and line['balance'] * line.get('change_sign',1.0) or 0.0, digits=2, grouping=True) or ''}</td>
                    </tr>
                %endif
            %endfor
        </tbody>
    </table>
    %endfor
</body>
</html>
