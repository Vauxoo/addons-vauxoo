<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>

<body style="border:0; margin: 0;" onload="subst()" >
    %for ifrs in objects :
          <table class="basic_table" >
            <tr>
                <td width="30%">
                    <div>${helper.embed_image('jpeg',str(ifrs.company_id.logo),250, 120)}</div>
                </td>
                <td>
                    <table style="border-bottom: 0px solid black; width: 100%; text-align:center;">
                        <tr><td><div class="td_company"><b>${ifrs.name or ''|entity}</b></div></td></tr>
                        <tr><td><div class="td_company">${ifrs.company_id.name or ''|entity}</div></td></tr>
                        <tr><td><div class="td_company">${ifrs._get_period_print_info(data['period'],data['report_type']) }</div></td></tr>
                        <tr><td><div class="td_company">${ifrs.fiscalyear_id.name or ''|entity}</div></td></tr>
                    </table>
                </td>
            </tr>
        </table>
        <br clear="all"/>
        
        <table class="list_table" width="90%">
            %if data['report_type'] == 'per':
                <% 
                    info = ifrs.get_report_data( data['fiscalyear'], data['exchange_date'], data['currency_wizard'], data['target_move'], data['period'],two=False)
                    num_month = ifrs.get_num_month(data['fiscalyear'], data['period'])
                %>
                %for ifrs_l in info:
                <tbody>
                     %if not ifrs_l.get('invisible'):
                        <td class="celda2">
                            ${ifrs_l.get('name')}
                        </td>
                        <td class="celda">
                            ${ifrs_l.get('type')=='detail' and formatLang( ifrs_l['period'].get(num_month,0.0), digits=2, date=False, date_time=False, grouping=3, monetary=False) or ''|entity}
                        </td>
                        <td class="celda">
                            <b>
                                ${ifrs_l.get('type')=='total' and  formatLang( ifrs_l['period'].get(num_month,0.0), digits=2, date=False, date_time=False, grouping=3, monetary=False) or ''|entity}
                            </b>
                        </td>
                      %endif
                </tbody>
                %endfor
            %else:
                <% 
                    info = ifrs.get_report_data( data['fiscalyear'], data['exchange_date'], data['currency_wizard'], data['target_move'], data['period'],two=True)
                %>
                %for ifrs_l in info:
                <tbody>
                     %if not ifrs_l.get('invisible'):
                        <td class="celda2">
                            ${ifrs_l.get('name')}
                        </td>
                        <td class="celda">
                            ${ifrs_l.get('type')=='detail' and formatLang( ifrs_l.get('amount'), digits=2, date=False, date_time=False, grouping=3, monetary=False) or ''|entity}
                        </td>
                        <td class="celda">
                            <b>
                                ${ifrs_l.get('type')=='total' and  formatLang( ifrs_l.get('amount'), digits=2, date=False, date_time=False, grouping=3, monetary=False) or ''|entity}
                            </b>
                        </td>
                      %endif
                </tbody>
                %endfor
            %endif
        </table>
    %endfor
</body>
</html>
