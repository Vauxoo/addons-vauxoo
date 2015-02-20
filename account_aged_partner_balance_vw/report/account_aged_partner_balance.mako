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
                                <th class="celdaBoxUp" style="text-align:center;" width="10%">${obj.chart_account_id.name or ''}</th>
                                <th class="celdaBoxUp" style="text-align:center;" width="10%">${obj.fiscalyear_id.name or ''}</th>
                                <th class="celdaBoxUp" style="text-align:center;" width="10%">${obj.date_from or ''}</th>
                                <th class="celdaBoxUp" style="text-align:center;" width="10%">${obj.period_length or ''}</th>
                                
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
                        <th class="celdaTituloTablaCompany" width="100%">${obj.company_id.name or ''} (Expressed in ${obj.company_id.currency_id.name } )</th>
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
                        <%tot_not_due = tot_01to30 = tot_31to60 = tot_61to90 = tot_91to120 = tot_121togr = tot_total = 0%>
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
                            <%
                            tot_not_due += line.not_due
                            tot_01to30 += line.days_due_01to30
                            tot_31to60 += line.days_due_31to60
                            tot_61to90 += line.days_due_61to90
                            tot_91to120 += line.days_due_91to120
                            tot_121togr += line.days_due_121togr
                            tot_total += line.total
                            %>
                        %endfor
                        <tr class="prueba">
                                <td class="celdaGrandTotal" width="30%">${_('Total')}</td>
                                <td class="celdaGrandTotal" width="10%">
                                    ${tot_not_due}
                                </td>
                                <td class="celdaGrandTotal" width="10%">
                                    ${tot_01to30}
                                </td>
                                <td class="celdaGrandTotal" width="10%">
                                    ${tot_31to60}
                                </td>
                                <td class="celdaGrandTotal" width="10%">
                                    ${tot_61to90}
                                </td>
                                <td class="celdaGrandTotal" width="10%">
                                    ${tot_91to120}
                                </td>
                                <td class="celdaGrandTotal" width="10%">
                                    ${tot_121togr}
                                </td>
                                <td class="celdaGrandTotal" width="10%">
                                    ${tot_total}
                                </td>
                            </tr>
                    </tbody>
                </table>
            %endif
            <%
            group_user = True
            show_aml = True
            partner_ids = []
            for wiz in obj.wizard_ids:
                group_user = wiz.group_user
                show_aml = wiz.show_aml
                partner_ids = wiz.partner_ids and [x.id for x in wiz.partner_ids] or wiz.partner_ids_default and [x.id for x in wiz.partner_ids_default] or []
                
            def get_dict_lines_by_partner(lines):
                dic_partner_lines = {}
                for line in lines:
                    if line.partner_id.id in partner_ids and line.partner_id.id:
                        doc = line.document_id
                        partner_name = line.partner_id.vat_split and line.partner_id.vat_split + ' - ' + line.partner_id.name or line.partner_id.name
                        if show_aml or (not show_aml and doc._name != 'account.move.line'):
                            if not group_user:
                                if partner_name in dic_partner_lines:
                                    dic_partner_lines.get(partner_name).append(line)
                                else:   
                                    dic_partner_lines.update({partner_name : [line]})
                            else:
                                user_id = doc._name == 'account.invoice' and doc.user_id and doc.user_id.name or doc.partner_id and doc.partner_id.user_id and doc.partner_id.user_id.name or "Not User"
                                if user_id in dic_partner_lines:
                                    dict_user = dic_partner_lines.get(user_id)
                                    if partner_name in dict_user:
                                        dic_partner_lines.get(user_id).get(partner_name).append(line)
                                    else:   
                                        dic_partner_lines.get(user_id).update({partner_name : [line]})
                                else:   
                                    dic_partner_lines.update({user_id : {partner_name : [line]}})
                return dic_partner_lines
            %>
            %if obj.type == "by_document":
                %if not group_user:
                    <%tot_not_due = tot_01to30 = tot_31to60 = tot_61to90 = tot_91to120 = tot_121togr = tot_residual= 0%>
                    %for partner in get_dict_lines_by_partner(obj.partner_doc_ids):
                        <%
                        lines_partner = get_dict_lines_by_partner(obj.partner_doc_ids).get(partner, False)
                        %>
                        %if lines_partner:
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
                                        <th class="celdaTituloTabla" style="text-align:left;" width="6%">${_('Not Due')}</th>
                                        <th class="celdaTituloTabla" style="text-align:left;" width="6%">${_('Due Days')}</th>
                                        <th class="celdaTituloTabla" style="text-align:left;" width="8%">${_('Residual')}</th>
                                        <% form = data['form']%>
                                        %for i in range (4,-1,-1):
                                            <th class="celdaTituloTabla" style="text-align:center;">${form.get('%i'%i).get('name')}</th>
                                        %endfor
                                    </tr>
                                </thead>
                                <tbody>
                                    <%to0130 = to3160 = to6190 = to91120 = to121 = residual = to_not_due = 0%>
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
                                        to_not_due += line.not_due
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
                                            <td class="celdaLineData" style="text-align:center;" width="6%">
                                                ${line.not_due}
                                            </td>
                                            <td class="celdaLineData" style="text-align:center;" width="6%">
                                                ${line.due_days}
                                            </td>
                                            <td class="celdaLineData" width="8%">
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
                                        <td class="celdaTotalTotales" width="10%"></td>
                                        <td class="celdaTotalTotales" style="text-align:center;" width="6%">
                                            ${formatLang(to_not_due, digits=2, grouping=True)}
                                        </td>
                                        <td class="celdaTotalTotales" style="text-align:center;" width="6%"></td>
                                        <td class="celdaTotalTotales" width="8%">
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
                            <%
                            tot_residual += residual
                            tot_not_due += to_not_due
                            tot_01to30 += to0130
                            tot_31to60 += to3160
                            tot_61to90 += to6190
                            tot_91to120 += to91120
                            tot_121togr += to121%>
                        %endif
                    %endfor
                    <table width="100%" border="0">
                        <tr class="prueba" >
                            <td class="celdaGrandTotal" width="20%">
                                ${_('Grand Total')}
                            </td>
                            <td class="celdaGrandTotal" width="10%"></td>
                            <td class="celdaGrandTotal" style="text-align:center;" width="6%">
                                ${formatLang(tot_not_due, digits=2, grouping=True)}
                            </td>
                            <td class="celdaGrandTotal" style="text-align:center;" width="6%"></td>
                            <td class="celdaGrandTotal" width="8%">
                                ${formatLang(tot_residual, digits=2, grouping=True)}
                            </td>
                            <td class="celdaGrandTotal" width="10%">
                                ${formatLang(tot_01to30, digits=2, grouping=True)}
                            </td>
                            <td class="celdaGrandTotal" width="10%">
                                ${formatLang(tot_31to60, digits=2, grouping=True)}
                            </td>
                            <td class="celdaGrandTotal" width="10%">
                                ${formatLang(tot_61to90, digits=2, grouping=True)}
                            </td>
                            <td class="celdaGrandTotal" width="10%">
                                ${formatLang(tot_91to120, digits=2, grouping=True)}
                            </td>
                            <td class="celdaGrandTotal" width="10%">
                                ${formatLang(tot_121togr, digits=2, grouping=True)}
                            </td>
                        </tr>
                    </table>
                %else:
                    <%ban = 1%>
                    <%tot_not_due = tot_01to30 = tot_31to60 = tot_61to90 = tot_91to120 = tot_121togr = tot_residual= 0%>
                    %for user in get_dict_lines_by_partner(obj.partner_doc_ids):
                        <table class="list_table"  width="100%" border="0">
                            <thead>
                                <tr>
                                    %if ban % 2 == 0:
                                        <th class="celdaTituloTablaUser" bgcolor="#DF013A" style="text-align:left;" width="10%">${user}</th>
                                    %else:
                                        <th class="celdaTituloTablaUser" bgcolor="#0174DF" style="text-align:left;" width="10%">${user}</th>
                                    %endif
                                </tr>
                            </thead>
                        </table>
                        %for partner in get_dict_lines_by_partner(obj.partner_doc_ids).get(user, False):
                            <%
                            lines_partner = get_dict_lines_by_partner(obj.partner_doc_ids).get(user).get(partner, False)
                            %>
                            %if lines_partner:
                                <table class="table_user"  width="100%" border="0">
                                    <thead>
                                        <tr>
                                            %if ban % 2 == 0:
                                                <th style="text-align:left;" bgcolor="#DF013A" width="0.5%"></th>
                                            %else:
                                                <th style="text-align:left;" bgcolor="#0174DF" width="0.5%"></th>
                                            %endif
                                            <th class="celdaTituloPartner" style="text-align:left;" width="0.5%">${partner}</th>
                                        </tr>
                                    </thead>
                                </table>
                                <table class="list_table"  width="100%" border="0">
                                    <thead>
                                        <tr>
                                            %if ban % 2 == 0:
                                                <th style="text-align:left;" bgcolor="#DF013A" width="0.5%"></th>
                                            %else:
                                                <th style="text-align:left;" bgcolor="#0174DF" width="0.5%"></th>
                                            %endif
                                            <th class="celdaTituloTabla" style="text-align:left;" width="19.5%">${_('Document')}</th>
                                            <th class="celdaTituloTabla" style="text-align:left;" width="10%">${_('Type')}</th>
                                            <th class="celdaTituloTabla" style="text-align:left;" width="6%">${_('Not Due')}</th>
                                            <th class="celdaTituloTabla" style="text-align:left;" width="6%">${_('Due Days')}</th>
                                            <th class="celdaTituloTabla" style="text-align:left;" width="8%">${_('Residual')}</th>
                                            <% form = data['form']%>
                                            %for i in range (4,-1,-1):
                                                <th class="celdaTituloTabla" style="text-align:center;">${form.get('%i'%i).get('name')}</th>
                                            %endfor
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <%
                                        to0130 = to3160 = to6190 = to91120 = to121 = residual = to_not_due = 0%>
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
                                            to_not_due += line.not_due
                                            %>
                                            <tr class="prueba" >
                                                %if ban % 2 == 0:
                                                    <th style="text-align:left;" bgcolor="#DF013A" width="0.5%"></th>
                                                %else:
                                                    <th style="text-align:left;" bgcolor="#0174DF" width="0.5%"></th>
                                                %endif
                                                <td class="celdaLineDataTitulo" width="19.5%">
                                                    ${document}
                                                </td>
                                                <td class="celdaLineData" width="10%">
                                                    ${type}
                                                </td>
                                                <td class="celdaLineData" style="text-align:center;" width="6%">
                                                    ${line.not_due}
                                                </td>
                                                <td class="celdaLineData" style="text-align:center;" width="6%">
                                                    ${line.due_days}
                                                </td>
                                                <td class="celdaLineData" width="8%">
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
                                            %if ban % 2 == 0:
                                                <th style="text-align:left;" bgcolor="#DF013A" width="0.5%"></th>
                                            %else:
                                                <th style="text-align:left;" bgcolor="#0174DF" width="0.5%"></th>
                                            %endif
                                            <td class="celdaTotalTotales" width="19.5%">
                                                ${_('Total')}
                                            </td>
                                            <td class="celdaTotalTotales" width="10%"></td>
                                            <td class="celdaTotalTotales" width="6%">
                                                ${formatLang(to_not_due, digits=2, grouping=True)}
                                            </td>
                                            <td class="celdaTotalTotales" width="6%"></td>
                                            <td class="celdaTotalTotales" width="8%">
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
                                <%
                                tot_residual += residual
                                tot_not_due += to_not_due
                                tot_01to30 += to0130
                                tot_31to60 += to3160
                                tot_61to90 += to6190
                                tot_91to120 += to91120
                                tot_121togr += to121%>
                            %endif
                        %endfor
                        <%ban += 1%>
                    %endfor
                    <table width="100%" border="0">
                        <tr>
                            <td class="celdaGrandTotal" width="20%">
                                ${_('Grand Total')}
                            </td>
                            <td class="celdaGrandTotal" width="10%"></td>
                            <td class="celdaGrandTotal" width="6%">
                                ${formatLang(tot_not_due, digits=2, grouping=True)}
                            </td>
                            <td class="celdaGrandTotal" width="6%"></td>
                            <td class="celdaGrandTotal" width="8%">
                                ${formatLang(tot_residual, digits=2, grouping=True)}
                            </td>
                            <td class="celdaGrandTotal" width="10%">
                                ${formatLang(tot_01to30, digits=2, grouping=True)}
                            </td>
                            <td class="celdaGrandTotal" width="10%">
                                ${formatLang(tot_31to60, digits=2, grouping=True)}
                            </td>
                            <td class="celdaGrandTotal" width="10%">
                                ${formatLang(tot_61to90, digits=2, grouping=True)}
                            </td>
                            <td class="celdaGrandTotal" width="10%">
                                ${formatLang(tot_91to120, digits=2, grouping=True)}
                            </td>
                            <td class="celdaGrandTotal" width="10%">
                                ${formatLang(tot_121togr, digits=2, grouping=True)}
                            </td>
                        </tr>
                    </table>
                %endif
            %endif
        %endfor
    </body>
</html>
