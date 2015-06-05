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
            <td class="celdaTituloTabla" style="text-align:right;" width="10%">${_('CODE')}</td>
            <td class="celdaTituloTabla" width="50%">${_('ACCOUNT')}</td>
            <td class="celdaTituloTabla" style="text-align:center;" width="10%">${_('INICIAL')}</td>
            <td class="celdaTituloTabla" style="text-align:center;" width="10%">${_('DEBIT')}</td>
            <td class="celdaTituloTabla" style="text-align:center;" width="10%">${_('CREDIT')}</td>
            <td class="celdaTituloTabla" style="text-align:center;" width="10%">${_('BALANCE')}</td>
        </tr>
    </thead>
</table>
<table width="100%">
     <thead>
        <tr>
            <td class="celdaTituloTabla" style="text-align:left;" width="10%">${_('DATE')}</td>
            <td class="celdaTituloTabla" width="10%">${_('PERIOD')}</td>
            <td class="celdaTituloTabla" width="40%">${_('JOURNAL ENTRY')}</td>
            <td class="celdaTituloTabla" width="40%"></td>
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
                        <td class="celdaLineDataTotal" width="10%">${(line['total']==True) and formatLang(line['balanceinit'] and line['balanceinit'] * line.get('change_sign',1.0) or 0.0, digits=2, grouping=True)  or ''}</td>
                        <td class="celdaLineDataTotal" width="10%"> ${(line['total']==True) and formatLang(line['debit'], digits=2, grouping=True) or ''}</td>
                        <td class="celdaLineDataTotal" width="10%">${(line['total']==True) and formatLang(line['credit'], digits=2, grouping=True) or ''}</td>
                        <td class="celdaLineDataTotal" width="10%">${(line['total']==True) and formatLang(line['balance'] and line['balance'] * line.get('change_sign',1.0) or 0.0, digits=2, grouping=True) or ''}</td>
                    </tr>
                 </tbody>
                %if line.has_key('journal'):
                    %for j in line['journal']:
                        <tbody>       
                            <tr>
                                <td class="celdaLineData" style="text-align:left;" width="10%" height="12pt">${formatLang( j['date'], date=True) or ''}</td>
                                <td class="celdaLineData" style="text-align:left;" width="10%">${j['period'] or ''}</td>
                                <td class="celdaLineDataNamePartner" colspan="4">${j['name'] or ''}</td>
                                <td class="celdaLineDataNamePartner" colspan="4"></td>
                            </tr>
                        </tbody>
                        %for k in j.get('obj').line_id:
                            <tbody> 
                                %if k.account_id.name.upper() == line['name'].upper() :
                                    <tr>
                                        <td class="celdaLineDataAccountSimilar" style="text-align:left;" colspan="2">${k.name or ''}</td>
                                        <td class="celdaLineDataAccountSimilar" style="text-align:left;">${k.ref and k.ref or ''}</td>
                                        <td class="celdaLineDataAccountSimilar" colspan="2">${k.partner_id and k.partner_id.name or ''}</td>
                                        <td class="celdaLineDataAccountSimilar" style="text-align:left;">${k.account_id and k.account_id.code or ''}</td>
                                        <td class="celdaLineDataAccountSimilar" style="text-align:left;" >${k.account_id and k.account_id.name or ''}</td>
                                        <td class="celdaLineDataAccountSimilar" style="text-align:right;" >${k.debit and formatLang(k.debit, digits=2, grouping=True) or ''}</td>
                                        <td class="celdaLineDataAccountSimilar" style="text-align:right;" >${k.credit and formatLang(k.credit, digits=2, grouping=True) or ''}</td>
                                        <td class="celdaLineDataAccountSimilar" style="text-align:right;" >${k.reconcile_id and k.reconcile_id.name or k.reconcile_partial_id and k.reconcile_partial_id.name or ''}</td>
                                    </tr>
                                %else:
                                    <tr>
                                        <td class="celdaLineDataAccount" style="text-align:left;" colspan="2">${k.name or ''}</td>
                                        <td class="celdaLineDataAccount" style="text-align:left;" >${k.ref and k.ref or ''}</td>
                                        <td class="celdaLineDataAccount" colspan="2">${k.partner_id and k.partner_id.name or ''}</td>
                                        <td class="celdaLineDataAccount" style="text-align:left;" >${k.account_id and k.account_id.code or ''}</td>
                                        <td class="celdaLineDataAccount" style="text-align:left;" >${k.account_id and k.account_id.name or ''}</td>
                                        <td class="celdaLineDataAccount" style="text-align:right;" >${k.debit and formatLang(k.debit, digits=2, grouping=True) or ''}</td>
                                        <td class="celdaLineDataAccount" style="text-align:right;" >${k.credit and formatLang(k.credit, digits=2, grouping=True) or ''}</td>
                                        <td class="celdaLineDataAccount" style="text-align:right;" >${k.reconcile_id and k.reconcile_id.name or k.reconcile_partial_id and k.reconcile_partial_id.name or ''}</td>
                                    </tr>
                                %endif
                            </tbody>
                        %endfor
                    %endfor
                %endif
            %endif
        %endfor
</table>

%endfor

</body>
</html>
