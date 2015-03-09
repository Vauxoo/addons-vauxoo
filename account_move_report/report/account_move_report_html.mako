<html>
    <head>
        <style type="text/css">
            ${css}
        </style>
    </head>
    <body>
        %for o in objects :
        <table width = '100%' class='table'>
            <tr>
                <td style="vertical-align: top;">
                    ${helper.embed_image('jpeg',str(o.company_id.logo),180, 85)}
                </td>
                <td class='dir_font'>
                    <div class='company_font'>${o.company_id.name or ''|entity}</div>
                    <br>${o.company_id.partner_id.street or ''|entity} No. 
                                                ${o.company_id.partner_id.street2 or ''|entity}
                                                ${o.company_id.partner_id.zip or ''|entity}
                                                <br/>${o.company_id.partner_id.city or ''|entity}
                                                , ${o.company_id.partner_id.state_id.name or ''|entity}
                                                , ${o.company_id.partner_id.country_id.name or ''|entity}
                </td>
                <td class='date_font'>
                    <div>${_("Printing Date:")} ${time.strftime('%Y-%m-%d %H:%M:%S')}</div>
                </td>

            </tr>
        </table>                                   

        <table>
            <tr>
                    <div>${_("Journal Entries: ")} ${o.name or '' |entity}</div>

            </tr>
            <tr>
                    <div>${_("Reference: ")} ${o.ref or '' |entity}</div>
            </tr>
            <tr>
                    <div>${_("Date: ")} ${o.date or '' |entity}</div>
            </tr>
            
        </table>
        
        <table width= '100%' class='title'>
            <tr>
                <td width='14%'>
                    <div>${_("Name")}</div>
                </td>
                <td width='14%'>
                    <div>${_("Partner")}</div>
                </td>
            <td width='27%'>
                    <div>${_("Account")}</div>
                </td>
                <td width='7%'>
                    <div>${_("Due date")}</div>
                </td>
                <td width='12%'>
                    <div>${_("Debit")}</div>
                </td>
                <td width='12%'>
                    <div>${_("Credit")}</div>
                </td>
                <td width='14%'>
                    <div>${_("Analytic Account")}</div>
                </td>
            </tr>
        </table>

        <table width= '100%' class='table'>
            %for line in o.line_id:
            <tr>
                <td width='14%' class='basic_td'>
                    <div>${line.name or '' |entity}</div>
                </td>
                <td width='14%' class='basic_td'>
                    <div>${line.partner_id.name or ''}</div>
                </td>
                <td width='27%' class='basic_td'>
                    <div>${line.account_id.code or '' |entity} - ${line.account_id.name or '' |entity}</div>
                </td>
                <td width='7%' class='basic_td'>
                    <div>${line.date_maturity or '' |entity}</div>
                </td>
                <td width='12%' class='basic_td' style="text-align:right;">
                    <div>${line.debit or '0.00' |entity}</div>
                </td>
                <td width='12%' class='basic_td' style="text-align:right;">
                    <div>${line.credit or '0.00' |entity}</div>
                </td>
                <td width='14%' class='basic_td'>
                    <div>${line.analytic_account_id.name or '' |entity}</div>
                </td>
            </tr>
            %endfor
        </table>
        <table width= '100%' class='table'>
            <tr>
                <td width='14%'></td>
                <td width='37%'></td>
                <td width='7%'></td>
                <td style="border-top:1px solid #000000; text-align:right;" class='basic_td'>
                    <div width='14%' >${formatLang(get_total_debit_credit(o.line_id)['sum_tot_debit']) or '0.00' |entity}</div>
                </td>
                <td style="border-top:1px solid #000000; text-align:right;" class='basic_td'>
                    <div width='14%'>${formatLang(get_total_debit_credit(o.line_id)['sum_tot_credit']) or '0.00' |entity}</div>
                </td>
                <td width='14%'></td>
            </tr>
            
        </table>
        %if len(loop._iterable) != 1 and loop.index != len(loop._iterable)-1:
            <p style="page-break-after:always"></p>
        %endif
    %endfor
    </body>
</html>
