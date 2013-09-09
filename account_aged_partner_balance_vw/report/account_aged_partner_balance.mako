<html>
    <head>
        <style type="text/css">
            ${css}
        </style>
    </head>
    <body style="border:0; margin: 0;" onload="subst()" >
        %for obj in objects :
            <table>
                <tr>
                    <td width="10%">
                        <div>${helper.embed_image('jpeg',str(obj.company_id.logo),220, 100)}</div>
                    </td>
                    <td>
                        <table style="width: 100%; text-align:center;">
                            <tr>
                                <th class="celdaTituloTabla" style="text-align:center;" width="10%">${_('Chart of Accounts')}</th>
                                <th class="celdaTituloTabla" style="text-align:center;" width="10%">${_('Fiscal Year')}</th>
                                <th class="celdaTituloTabla" style="text-align:center;" width="10%">${_('Start Date')}</th>
                                <th class="celdaTituloTabla" style="text-align:center;" width="10%">${_('Period Length(days)')}</th>
                                <th class="celdaTituloTabla" style="text-align:center;" width="10%">${_('Partners ')}</th>
                                <th class="celdaTituloTabla" style="text-align:center;" width="10%">${_('Analysis Direction')}</th>
                                <th class="celdaTituloTabla" style="text-align:center;" width="10%">${_('Target Moves')}</th>
                            </tr>
                            <tr>
                                <th class="celdaBoxUp" style="text-align:center;" width="10%">${obj.chart_account_id.name or ''|entity}</th>
                                <th class="celdaBoxUp" style="text-align:center;" width="10%">${obj.fiscalyear_id.name or ''|entity}</th>
                                <th class="celdaBoxUp" style="text-align:center;" width="10%">${obj.date_from or ''|entity}</th>
                                <th class="celdaBoxUp" style="text-align:center;" width="10%">${obj.period_length or ''|entity}</th>
                                
                                %if obj.result_selection == 'customer':
                                    <th class="celdaBoxUp" style="text-align:center;" width="10%">${_('Receivable Accounts')}</th>
                                    %elif obj.result_selection == 'supplier':
                                    <th class="celdaBoxUp" style="text-align:center;" width="10%">${_('Payable Accounts')}</th>
                                    %elif obj.result_selection == 'customer_suppiler':
                                    <th class="celdaBoxUp" style="text-align:center;" width="10%">${_('Receivable and Payable Accounts')}</th>
                                %endif
                                %if obj.direction_selection == 'past':
                                <th class="celdaBoxUp" style="text-align:center;" width="10%">${_('Past')}</th>
                                    %elif obj.direction_selection == 'future':
                                    <th class="celdaBoxUp" style="text-align:center;" width="10%">${_('Future')}</th>
                                %endif
                                %if obj.target_move == 'posted':
                                <th class="celdaBoxUp" style="text-align:center;" width="10%">${_('All Posted Entries')}</th>
                                    %elif obj.target_move == 'all':
                                    <th class="celdaBoxUp" style="text-align:center;" width="10%">${_('All Entries')}</th>
                                %endif
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
            <br clear="all"/>
            
            <table class="list_table"  width="100%" border="0">
                <thead>
                    <tr>
                        <th class="celdaTituloTabla" width="100%">${obj.company_id.name or ''|entity} (Expressed in ${obj.company_id.currency_id.name |entity} )</th>
                    </tr>
                </thead>
            </table>
            <table class="list_table"  width="100%" border="0">
                <thead>
                    <tr>
                        <th class="celdaTituloTabla" style="text-align:center;" width="30%">${_('Partners')}</th>
                        <th class="celdaTituloTabla" style="text-align:center;" width="10%">${_('Not due')}</th>
                        <% form = data['form']%>
                        %for i in range (4,-1,-1):
                            <th class="celdaTituloTabla" style="text-align:center;">${form.get('%i'%i).get('name')}</th>
                        %endfor
                        <th class="celdaTituloTabla" style="text-align:center;">${_('Total')}</th>
                    </tr>
                </thead>
                 
                <tbody>
                    %for line in obj.partner_line_ids:
                        <tr class="prueba" >
                            <td class="celdaLineDataTitulo" width="30%">
                                ${line.partner_id.name.upper()}
                            </td>
                            <td class="celdaLineData" width="10%">
                                ${line.not_due}
                            </td>
                            <td class="celdaLineData" width="10%">
                                ${line.days_due_01to30}
                            </td>
                            <td class="celdaLineData" width="10%">
                                ${line.days_due_31to60}
                            </td>
                            <td class="celdaLineData" width="10%">
                                ${line.days_due_61to90}
                            </td>
                            <td class="celdaLineData" width="10%">
                                ${line.days_due_91to120}
                            </td>
                            <td class="celdaLineData" width="10%">
                                ${line.days_due_121togr}
                            </td>
                            <td class="celdaTotal" width="10%">
                                ${line.total}
                            </td>
                        </tr>
                    %endfor
                </tbody>
            </table>
        %endfor
    </body>
</html>
