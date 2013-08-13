<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>

<body style="border:0; margin: 0;" onload="subst()" >
    %for ifrs in objects :
          <table>
            <tr>
                <td width="30%">
                    <div>${helper.embed_image('jpeg',str(ifrs.company_id.logo),260, 120)}</div>
                </td>
                <td>
                    <table style="width: 100%; text-align:center;">
                        <tr><td><div class="td_company_title">${ifrs.company_id.name or ''|entity}</div></td></tr>
                        <tr><td><div class="td_company">${ifrs._get_period_print_info(data['period'],data['report_type']) }</div></td></tr>
                        <tr><td><div class="td_company">${ifrs.fiscalyear_id.name or ''|entity}</div></td></tr>
                    </table>
                </td>
            </tr>
        </table>
        <br clear="all"/>
        
        <table class="list_table"  width="100%" border="0">
            <thead>
                <tr>
                    <th class="celdaTituloTabla" width="100%">${ifrs.name or ''|entity} (Expressed in ${data['currency_wizard_name'] or ''|entity} @ ${data['exchange_date'] or ''|entity})</th>
                </tr>
            </thead>
        </table>
        <table class="list_table"  width="100%" border="0">
            <tbody>
                <% 
                    i=0
                %>
                %if data['report_type'] == 'per':
                    <% 
                        info = ifrs.get_report_data( data['fiscalyear'], data['exchange_date'], data['currency_wizard'], data['target_move'], data['period'],two=False)
                        num_month = ifrs.get_num_month(data['fiscalyear'], data['period'])
                    %>
                    %for ifrs_l in info:
                        <tr class="prueba" >
                            %if not ifrs_l.get('invisible'):
                                %if ifrs_l.get('type')=='total':
                                    <td class="celdaTotalTitulo" width="60%">
                                        ${ifrs_l.get('name').upper()}
                                    </td>
                                    <td class="celdaTotal" width="20%">
                                   </td>
                                    <td class="celdaTotal" width="20%">
                                        %if ifrs_l.get('comparison') in ('subtract', 'ratio', 'without'):
                                            %if ifrs_l.get('operator') in ('subtract', 'ratio', 'without', 'product'):
                                                %try:
                                                    ${ifrs_l.get('type')=='total' and  formatLang( ifrs_l['period'].get(num_month,0.0), digits=2, date=False, date_time=False, grouping=3, monetary=True) or ''|entity}
                                                %except:
                                                    0.0
                                                %endtry
                                            %elif ifrs_l.get('operator') == 'percent':
                                                %try:
                                                    ${ifrs_l.get('type')=='total' and formatLang(ifrs_l['period'].get(num_month,0.0), digits=2, date=False, date_time=False, grouping=3, monetary=True)} %
                                                %except:
                                                    0.0
                                                %endtry
                                            %endif
                                        %elif ifrs_l.get('comparison')== 'percent':
                                            %try:
                                                ${ifrs_l.get('type')=='total' and formatLang(ifrs_l['period'].get(num_month,0.0), digits=2, date=False, date_time=False, grouping=3, monetary=True)} %
                                            %except:
                                                0.0
                                            %endtry
                                        %endif
                                    </td>
                                %else:
                                    %if ifrs_l.get('type')=='detail':
                                        <td class="celdaDetailTitulo" width="60%">
                                            ${ifrs_l.get('name').capitalize()}
                                        </td>
                                        <td class="celdaDetail" width="20%">
                                            ${ifrs_l.get('type')=='detail' and formatLang( ifrs_l['period'].get(num_month,0.0), digits=2, date=False, date_time=False, grouping=3, monetary=True) or ''|entity}
                                        </td>
                                        <td class="celdaDetail" width="20%">
                                        </td>
                                    %else:
                                        %if ifrs_l.get('type')=='abstract':
                                            <td class="celdaAbstractTotal" width="60%">
                                                ${ifrs_l.get('name')}
                                            </td>
                                            <td class="celdaAbstract" width="20%"></td>
                                            <td class="celdaAbstract" width="20%"></td>
                                        %else:
                                            %if ifrs_l.get('type')=='constant':
                                                <td class="celdaDetailTitulo" width="15%">
                                                    ${ifrs_l.get('name').capitalize()}
                                                </td>
                                                <td class="celdaDetail" width="20%">
                                                    ${ifrs_l.get('type')=='constant' and formatLang( ifrs_l['period'].get(num_month,0.0), digits=0, date=False, date_time=False, grouping=3, monetary=False) or ''|entity}
                                                </td>
                                            %endif
                                        %endif
                                    %endif
                                %endif
                            %endif
                        </tr>
                        <% i+=1 %>
                    %endfor
                %else:
                    <% 
                        info = ifrs.get_report_data( data['fiscalyear'], data['exchange_date'], data['currency_wizard'], data['target_move'], data['period'],two=True)
                    %>
                    %for ifrs_l in info:
                        <tr class="prueba">
                             %if not ifrs_l.get('invisible'):
                                %if ifrs_l.get('type')=='total':
                                    <td class="celdaTotalTitulo" width="60%">
                                        ${ifrs_l.get('name').upper()}
                                    </td>
                                    <td class="celdaTotal" width="20%">
                                   </td>
                                    <td class="celdaTotal" width="20%">
                                        %if ifrs_l.get('comparison') in ('subtract', 'ratio', 'without'):
                                            %if ifrs_l.get('operator') in ('subtract', 'ratio', 'without', 'product'):
                                                %try:
                                                    ${ifrs_l.get('type')=='total' and  formatLang( ifrs_l.get('amount'), digits=2, date=False, date_time=False, grouping=3, monetary=True) or ''|entity}
                                                %except:
                                                    0.0
                                                %endtry
                                            %elif ifrs_l.get('operator') == 'percent':
                                                %try:
                                                    ${ifrs_l.get('type')=='total' and  formatLang( ifrs_l.get('amount'), digits=2, date=False, date_time=False, grouping=3, monetary=True) or ''|entity} %
                                                %except:
                                                    0.0
                                                %endtry
                                            %endif
                                        %elif ifrs_l.get('comparison')== 'percent':
                                            %try:
                                                ${ifrs_l.get('type')=='total' and  formatLang( ifrs_l.get('amount'), digits=2, date=False, date_time=False, grouping=3, monetary=True) or ''|entity} %
                                            %except:
                                                0.0
                                            %endtry
                                        %endif
                                    </td>
                                %else:
                                    %if ifrs_l.get('type')=='detail':
                                        <td class="celdaDetailTitulo" width="60%">
                                            ${ifrs_l.get('name').capitalize()}
                                        </td>
                                        <td class="celdaDetail" width="20%">
                                            ${ifrs_l.get('type')=='detail' and formatLang( ifrs_l.get('amount'), digits=2, date=False, date_time=False, grouping=3, monetary=False) or ''|entity}
                                        </td>
                                        <td class="celdaDetail" width="20%">
                                        </td>
                                    %else:
                                        %if ifrs_l.get('type')=='abstract':
                                            <td class="celdaAbstractTotal" width="60%">
                                                ${ifrs_l.get('name')}
                                            </td>
                                            <td class="celdaAbstract" width="20%"></td>
                                            <td class="celdaAbstract" width="20%"></td>
                                        %else:
                                            %if ifrs_l.get('type')=='constant':
                                                <td class="celdaDetailTitulo" width="15%">
                                                    ${ifrs_l.get('name').capitalize()}
                                                </td>
                                                <td class="celdaDetail" width="20%">
                                                    ${ifrs_l.get('type')=='constant' and formatLang( ifrs_l.get('amount'), digits=0, date=False, date_time=False, grouping=3, monetary=False) or ''|entity}
                                                </td>
                                                <td class="celdaDetail" width="20%">
                                            %endif
                                        %endif
                                    %endif
                                %endif
                            %endif
                          </tr>
                          <% i+=1 %>
                    %endfor
                %endif
            </tbody>
        </table>
    %endfor
</body>
</html>
