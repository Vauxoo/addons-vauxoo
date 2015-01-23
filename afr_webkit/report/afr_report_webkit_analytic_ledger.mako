<!DOCTYPE>
<html>
<head>
<style type="text/css">                                                                         
    ${css}
</style>
</head>

<body style="border:0; margin: 0;" onload="subst()" >
%for obj in objects:
<table width="100%">
    <tr>
        <td>
            <div>${helper.embed_image('jpeg',str(obj.company_id.logo),250, 120)}</div>
        </td>
        <td>
            <table style="width: 100%; text-align:center;">
                <tr><td><div class="td_company_title">${obj.company_id.name or ''}</div></td></tr>
                <tr><td><div class="td_company">${obj.get_parser_method('get_vat_by_country',data['form']) or ''}</div></td></tr>
                <tr><td><div class="td_company">${obj.get_parser_method('get_informe_text',data['form']) or ''}</div></td></tr>
                <tr><td><div class="td_company">${_(Expressed in data['form'] and (' %s'% obj.get_parser_method('exchange_name',data['form'])) or '')}</div></td></tr>
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
<table width="100%">
    <thead>
        <tr>
            <td class="celdaTituloTabla" style="text-align:right" width="10%">${_('CODE')}</td>
            <td class="celdaTituloTabla" width="50%">${_('ACCOUNT')}</td>
            <td class="celdaTituloTabla" width="10%" style="text-align:center;" >${_('INICIAL')}</td>
            <td class="celdaTituloTabla" width="10%" style="text-align:center;" >${_('DEBIT')}</td>
            <td class="celdaTituloTabla" width="10%" style="text-align:center;" >${_('CREDIT')}</td>
            <td class="celdaTituloTabla" width="10%" style="text-align:center;" >${_('BALANCE')}</td>
        </tr>
    </thead>
</table>
<table width="100%">
    <thead>
        <tr>
            <td class="celdaTituloTabla" style="text-align:left;" width="10%">${_('DATE')}</td>
            <td class="celdaTituloTabla" width="10%">${_('PERIOD')}</td>
            <td class="celdaTituloTabla" width="20%">${_('REFERENCE')}</td>
            <td class="celdaTituloTabla" width="20%">${_('JOURNAL ENTRY')}</td>
            <td class="celdaTituloTabla" width="10%">${_('PARTNER')}</td>
            <td class="celdaTituloTabla" width="10%" ></td>
            <td class="celdaTituloTabla" width="10%" ></td>
            <td class="celdaTituloTabla" width="10%" ></td>
        </tr>
    </thead>
</table>
<table width="100%">
    <tr>
        <td width="10%"></td>
        <td width="10%"></td>
        <td width="10%"></td>
        <td width="10%"></td>
        <td width="10%"></td>
        <td width="10%"></td>
        <td width="10%"></td>
        <td width="10%"></td>
        <td width="10%"></td>
        <td width="10%"></td>
    </tr>
        %for line in obj.get_parser_method('lines',data['form']):
            %if line['type']!= 'view':   
                <tbody>     
                    <tr>
                        <td class="celdaLineDataTotal" style="text-align:right;font-style:italic;" width="10%">${line['label'] == True and line['code'] or ''}</td>
                        <td class="celdaLineDataNameTotal" colspan="5">${line['name'].upper() or line['name'].title() or ''}</td>
                        <td class="celdaLineDataTotal" width="10%" style="text-align:right;">${(line['total']==True) and formatLang(line['balanceinit'] and line['balanceinit'] * line.get('change_sign',1.0) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineDataTotal" width="10%" style="text-align:right;">${(line['total']==True) and formatLang(line['debit'], digits=2, grouping=True) or ''}</td>
                        <td class="celdaLineDataTotal" width="10%" style="text-align:right;">${(line['total']==True) and formatLang(line['credit'], digits=2, grouping=True) or ''}</td>
                        <td class="celdaLineDataTotal" width="10%" style="text-align:right;">${(line['total']==True) and formatLang(line['balance'] and line['balance'] * line.get('change_sign',1.0) or 0.0, digits=2, grouping=True) or ''}</td>
                    </tr>
                </tbody>
                %for m in line['mayor']:
                    <tbody>
                        <tr>
                            <td class="celdaLineData" style="text-align:left;font-style:italic;" width="10%">${formatLang( m['date'], date=True) or ''}</td>
                            <td class="celdaLineData" style="text-align:left;" width="10%">${m['period'] or ''}</td>
                            <td class="celdaLineDataNamePartner" colspan="2">${m['name'] or ''} ${m['ref'] and (' - Ref %s'%m['ref']) or ''}</td>
                            <td class="celdaLineDataNamePartner" colspan="2">${m['entry'] or ''}</td>
                            <td class="celdaLineDataNamePartner" width="10%">${m['partner']  or ''}</td>
                            <td class="celdaLineDataNamePartner" width="10%">${(line['total']==True) and formatLang(m['debit'], digits=2, grouping=True) or ''}</td>
                            <td class="celdaLineDataNamePartner" width="10%">${(line['total']==True) and formatLang(m['credit'], digits=2, grouping=True) or ''}</td>
                            <td class="celdaLineDataNamePartner" width="10%">${(line['total']==True) and formatLang(m['balance'] and m['balance'] * line.get('change_sign',1.0) or 0.0, digits=2, grouping=True) or ''}</td>
                        </tr>
                    </tbody>
                %endfor
            %endif
        %endfor
</table>

%endfor
</body>
</html>
