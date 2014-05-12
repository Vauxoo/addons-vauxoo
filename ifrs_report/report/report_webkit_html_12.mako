<!DOCTYPE>
<html>
<head>
    <style type="text/css">
        ${css}
    </style>

</head>

<body style="border:0; margin: 0;" onload="subst()">
    %for ifrs in objects :
    <table>
        <tr>
            <td width="30%">
                <div>${helper.embed_image('jpeg',str(ifrs.company_id.logo),250, 120)}</div>
            </td>
            <td width="70%">
                <table style="width: 100%; text-align:center;">
                    <tr><td><div class="td_company_title">${ifrs.company_id.name or ''|entity}</div></td></tr>
                    <tr><td><div class="td_company">${ifrs.fiscalyear_id.name or ''|entity}</div></td></tr>
                    <tr><td><div class="td_company">${ ifrs._get_period_print_info(data['period'],data['report_type']) }</div></td></tr>
                </table>
            </td>
            <td>
            </td>
        </tr>
    </table> 

    <table class="list_table"  width="100%" border="0">
        <thead>
            <tr>
                <th class="celdaTituloTabla" width="100%">${ifrs.name or ''|entity} (Expressed in ${data['currency_wizard_name'] or ''|entity} @ ${data['exchange_date'] or ''|entity})</th>
            </tr>
        </thead>
    </table>
    <table class="list_table" width="100%" >
        <%
            period_name = ifrs._get_periods_name_list(data['fiscalyear'])
        %>
        <thead>
            <tr>
                %for li in range(0, 13):
                    <th class="celda" style="text-align:center;">
                        %try:
                            ${ period_name[li][2] }
                        %except:
                            pass
                        %endtry
                    </th>
                %endfor
            </tr>
        </thead>
        
        <%
            info = ifrs.get_report_data( data['fiscalyear'], data['exchange_date'], data['currency_wizard'], data['target_move'])
            i = 0
        %>
        
        %for ifrs_l in info:
            <tbody>
            %if not info[i]['invisible']:
                <tr class="prueba">
                    %if info[i]['type']=='total':
                     <th class="celdaTotalTitulo" width="15%">${info[i].get('name').upper()}</th>
                            %for moth in range(1, 13): 
                            <th class="celdaTotal" width="8%">
                                %if ifrs_l.get('comparison') in ('subtract', 'ratio', 'without', False):
                                    %if ifrs_l.get('operator') in ('subtract', 'ratio', 'without', 'product', False):
                                        %try:
                                            ${formatLang(info[i]['period'][moth], digits=2, date=False, date_time=False, grouping=3, monetary=True)}
                                        %except:
                                            0.0
                                        %endtry
                                    %elif ifrs_l.get('operator') == 'percent':
                                        %try:
                                            ${formatLang(info[i]['period'][moth], digits=2, date=False, date_time=False, grouping=3, monetary=True)} %
                                        %except:
                                            0.0
                                        %endtry
                                    %endif
                                %elif ifrs_l.get('comparison')== 'percent':
                                    %try:
                                        ${formatLang(info[i]['period'][moth], digits=2, date=False, date_time=False, grouping=3, monetary=True)} %
                                    %except:
                                        0.0
                                    %endtry
                                %endif
                            </th>
                            %endfor
                    %else:
                         %if ifrs_l.get('type')=='detail':
                            <td class="celdaDetailTitulo" width="15%">
                                ${info[i].get('name').capitalize()}
                                </td>
                                %for moth in range(1, 13): 
                                <td class="celdaDetail" width="8%">
                                    %try:
                                        ${formatLang(info[i]['period'][moth], digits=2, date=False, date_time=False, grouping=3, monetary=True)}
                                    %except:
                                        0.0
                                    %endtry
                                </td>
                                %endfor
                        %else:
                            %if ifrs_l.get('type')=='abstract':
                                <td class="celdaAbstractTotal" width="15%">
                                    ${ifrs_l.get('name')}
                                </td>
                                %for moth in range(1, 13):
                                <td class="celdaAbstract" width="8%"></td> 
                                %endfor
                            %else:
                                %if ifrs_l.get('type')=='constant':
                                    <td class="celdaDetailTitulo" width="15%">
                                        ${ifrs_l.get('name').capitalize()}
                                    </td>
                                    %for moth in range(1, 13): 
                                        <td class="celdaDetail" width="8%">
                                            %try:
                                                ${formatLang(info[i]['period'][moth], digits=0, date=False, date_time=False, grouping=3, monetary=False)}
                                            %except:
                                                0.0
                                            %endtry
                                        </td>
                                    %endfor
                                %endif
                            %endif
                        %endif
                    %endif
                </tr>
            %endif
            <% i +=1 %>
        %endfor
        </tbody>
    </table>
    %endfor
</body>
</html>
