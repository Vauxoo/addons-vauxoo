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
            <td>
                <table class="dest_address " style="border-bottom: 0px solid black; width: 100%">
                    <tr><td><b>[${ifrs.code or ''|entity}] ${ifrs.name or ''|entity}</b></td></tr>
                    <tr><td>${ifrs.company_id.name or ''|entity}</td></tr>
                    <tr><td>${ifrs.fiscalyear_id.name or ''|entity}</td></tr>
                    <tr><td>${ ifrs._get_period_print_info(data['period'],data['report_type']) }</td></tr>
                </table>
            </td>
            <td>
            </td>
        </tr>
    </table> 


    <table class="list_table"  width="90%">
        <%
            period_name = ifrs._get_periods_name_list(data['fiscalyear'])
        %>
        <thead>
            <tr>
                %for li in range(0, 13):
                    <th class="celda">
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

        %while i < len(info):
            <tbody>
            %if not info[i]['invisible']:
                <tr class="prueba">
                    %if info[i]['type']=='total':
                    
                     <th class="celdaTotalTitulo">${info[i].get('name')}</th>
                            %for moth in range(1, 13): 
                            <th class="celdaTotal">
                                %try:
                                    ${formatLang(info[i]['period'][moth], digits=2, date=False, date_time=False, grouping=3, monetary=False)}
                                %except:
                                    0.0
                                %endtry
                            </th>
                            %endfor
                    %else:
                        %if i%2==0:
                        <th class="celda5">${info[i].get('name')}</th>
                            %for moth in range(1, 13): 
                            <th class="celda2">
                                %try:
                                    ${formatLang(info[i]['period'][moth], digits=2, date=False, date_time=False, grouping=3, monetary=False)}
                                %except:
                                    0.0
                                %endtry
                            </th>
                            %endfor
                        %else:
                             <th class="celda6">${info[i].get('name')}</th>
                            %for moth in range(1, 13): 
                            <th class="celda4">
                                %try:
                                    ${formatLang(info[i]['period'][moth], digits=2, date=False, date_time=False, grouping=3, monetary=False)}
                                %except:
                                    0.0
                                %endtry
                            </th>
                            %endfor
                        %endif
                    %endif
                </tr>
            %endif
            <% i +=1 %>
        %endwhile
        </tbody>
    </table>
    %endfor
</body>
</html>
