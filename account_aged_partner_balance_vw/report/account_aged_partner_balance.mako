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
                        <th class="celdaTituloTablaCompany" width="100%">${obj.company_id.name or ''|entity} (Expressed in ${obj.company_id.currency_id.name |entity} )</th>
                    </tr>
                </thead>
            </table>
            %if obj.type != "by_document":
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
                            
    <!--
                            Aquí va la celda de los totales la vemos si la ponemos con un ciclo por lo pronto te dejo 
                            El esqueleto de esos campos
    -->
                        <tr>
                            %for i in range(1,9):
                                <td class="celdaTotalTotales" >${_('$')}
                                </td>
                            %endfor
                        </tr>
                    </tbody>
                </table>
            %endif
            <%
            def get_dict_lines_by_partner(lines):
                dic_partner_lines = {}
                for line in lines:
                    if line.partner_id.id:
                        if line.partner_id.name in dic_partner_lines:
                            dic_partner_lines.get(line.partner_id.name).append(line)
                        else:   
                            dic_partner_lines.update({line.partner_id.name : [line]})
                return dic_partner_lines
            %>
            %if obj.type == "by_document":
                %for partner in get_dict_lines_by_partner(obj.partner_doc_ids):
                    <table class="list_table"  width="100%" border="0">
                        <thead>
                            <tr>
                                <th class="celdaTituloPartner" style="text-align:left;" width="10%">${partner}</th>
                            </tr>
                        </thead>
                    </table>
                    <table class="list_table"  width="100%" border="0">
                        <thead>
                            <tr>
                                <th class="celdaTituloTabla" style="text-align:left;" width="20%">${_('Document')}</th>
                                <th class="celdaTituloTabla" style="text-align:left;" width="10%">${_('Type')}</th>
                                <th class="celdaTituloTabla" style="text-align:left;" width="10%">${_('Due Days')}</th>
                                <th class="celdaTituloTabla" style="text-align:left;" width="10%">${_('Residual')}</th>
                                <% form = data['form']%>
                                %for i in range (4,-1,-1):
                                    <th class="celdaTituloTabla" style="text-align:center;">${form.get('%i'%i).get('name')}</th>
                                %endfor
                            </tr>
                        </thead>
                        
                        <tbody>
                            <%lines_partner = get_dict_lines_by_partner(obj.partner_doc_ids).get(partner, False)%>
                            <%
                            to0130 = 0
                            to3160 = 0
                            to6190 = 0
                            to91120 = 0
                            to121 = 0
                            residual = 0%>
                            %for line in lines_partner:
                                <%
                                type = ''
                                document = ''
                                if line.document_id._name == 'account.invoice':
                                    document = line.document_id.number
                                    type = 'Invoice'
                                elif line.document_id._name == 'account.voucher':
                                    type = 'Voucher'
                                    document = line.document_id.number
                                elif line.document_id._name == 'account.move.line':
                                    type = 'Journal Entry Line'
                                    document = line.document_id.name
                                to0130 += line.days_due_01to30
                                to3160 += line.days_due_31to60
                                to6190 += line.days_due_61to90
                                to91120 += line.days_due_91to120
                                to121 += line.days_due_121togr
                                residual += line.residual
                                %>
                                <tr class="prueba" >
                                    <td class="celdaLineDataTitulo" width="20%">
                                        ${document}
                                    </td>
                                    <td class="celdaLineData" width="10%">
                                        ${type}
                                    </td>
                                    <td class="celdaLineData" style="text-align:center;" width="10%">
                                        ${line.due_days}
                                    </td>
                                    <td class="celdaLineData" width="10%">
                                        ${line.residual}
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
                                </tr>
                            %endfor
                            <tr>
                                <td class="celdaTotalTotales" width="20%">
                                    ${_('Total')}
                                </td>
                                <td class="celdaTotalTotales" width="10%">
                                </td>
                                <td class="celdaTotalTotales" width="10%"></td>
                                <td class="celdaTotalTotales" width="10%">
                                    ${formatLang(residual, digits=2, grouping=True)}
                                </td>
                                <td class="celdaTotalTotales" width="10%">
                                    ${formatLang(to0130, digits=2, grouping=True)}
                                </td>
                                <td class="celdaTotalTotales" width="10%">
                                    ${formatLang(to3160, digits=2, grouping=True)}
                                </td>
                                <td class="celdaTotalTotales" width="10%">
                                    ${formatLang(to6190, digits=2, grouping=True)}
                                </td>
                                <td class="celdaTotalTotales" width="10%">
                                    ${formatLang(to91120, digits=2, grouping=True)}
                                </td>
                                <td class="celdaTotalTotales" width="10%">
                                    ${formatLang(to121, digits=2, grouping=True)}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                %endfor
            %endif
        %endfor
    </body>
</html>
