<html>
    <head>
        <style type="text/css">
            ${css}
        </style>
    </head>
    <body>
        %for o in objects :
        <table width = '100%' class='td_company_title'>
            <tr>
                <td style="vertical-align: top;max-height: 45px;">
                    ${helper.embed_image('jpeg',str(o.company_id.logo),180, 85)}
                </td>
                <td>
                    <div>${o.company_id.name or ''|entity}</div>
                    <br>${o.company_id.partner_id.street or ''|entity} No. 
                                                ${o.company_id.partner_id.street2 or ''|entity}
                                                ${o.company_id.partner_id.zip or ''|entity}
                                                <br/>${o.company_id.partner_id.city or ''|entity}
                                                , ${o.company_id.partner_id.state_id.name or ''|entity}
                                                , ${o.company_id.partner_id.country_id.name or ''|entity}
                </td>
                <td>
                    <div>${_("Printing Date:")} ${time.strftime('%Y-%m-%d %H:%M:%S')}</div>
                </td>
            </tr>
        </table>                                   

        <table class='celdaDetailTitulo'>
            <tr>
                <div>
                    <td>${_("Journal Entries: ")} ${o.name or '' |entity}</td>
                </div>
            </tr>
            <tr>
                <div>
                    <td>${_("Reference: ")} ${o.ref or '' |entity}</td>
                </div>
            </tr>
            <tr width= '100%'>
                <div>
                    <td width= '50%'>
                        ${_("Period: ")} ${o.period_id.name or '' |entity}
                    </td>
                    <td width= '50%'>
                        ${_("Date: ")} ${o.date or '' |entity}
                    </td>  
                </div>
            </tr>
            <tr>
                <div>
                    <td>${_("To Review: ")} ${o.to_check or '' |entity}</td>
                </div>
            </tr>
        </table>
        
        <table width= '100%' style="border-collapse: collapse;">
            <tr class='celdaTituloTabla'>
                <td width='5%'>
                    <div>${_("Invoice")}</div>
                </td>
                <td width='6%'>
                    <div>${_("Name")}</div>
                </td>
                <td width='7%'>
                    <div>${_("Partner")}</div>
                </td>
                <td width='8%'>
                    <div>${_("Account")}</div>
                </td>
                <td width='6%'>
                    <div>${_("Due date")}</div>
                </td>
                <td width='5%'>
                    <div>${_("Debit")}</div>
                </td>
                <td width='5%'>
                    <div>${_("Credit")}</div>
                </td>
                <td width='6%'>
                    <div>${_("Analytic Account")}</div>
                </td>
                <td width='6%'>
                    <div>${_("Amount Currency")}</div>
                </td>
                <td width='6%'>
                    <div>${_("Currency")}</div>
                </td>
                <td width='6%'>
                    <div>${_("Tax Account")}</div>
                </td>
                <td width='6%'>
                    <div>${_("Tax Amount")}</div>
                </td>
                <td width='6%'>
                    <div>${_("Not Consider in Diot")}</div>
                </td>
                <td width='6%'>
                    <div>${_("Status")}</div>
                </td>
                <td width='6%'>
                    <div>${_("Reconcile")}</div>
                </td>
            </tr>
            %for line in o.line_id:
            <tr class='celdaDetail'>
                <td width='5%'>
                    <div>${line.invoice.number or '' |entity}</div>
                </td>
                <td width='6%' style="word-wrap: break-word">
                    <div>${line.name or '' |entity}</div>
                </td>
                <td width='7%'>
                    <div>${line.partner_id.name or ''}</div>
                </td>
                <td width='8%'>
                    <div>${line.account_id.code or '' |entity} - ${line.account_id.name or '' |entity}</div>
                </td>
                <td width='6%'>
                    <div>${line.date_maturity or '' |entity}</div>
                </td>
                <td width='5%' style="text-align:right;">
                    <div>${line.debit or '0.00' |entity}</div>
                </td>
                <td width='5%' style="text-align:right;">
                    <div>${line.credit or '0.00' |entity}</div>
                </td>
                <td width='6%'>
                    <div>${line.analytic_account_id.name or '' |entity}</div>
                </td>
                <td width='6%' style="text-align:right;">
                    <div>${line.amount_currency or '' |entity}</div>
                </td>
                <td width='6%'>
                    <div>${line.currency_id.name or '' |entity}</div>
                </td>
                <td width='6%'>
                    <div>${line.tax_code_id.name or '' |entity}</div>
                </td>
                <td width='6%' style="text-align:right;">
                    <div>${line.tax_amount or '' |entity}</div>
                </td>
                <td width='6%' style="text-align:center;">
                    %if line.not_move_diot:
                        <p>&#10004;</p>
                    %endif
                </td>
                <td width='6%' style="text-align:center;">
                    <div>${line.state or '' |entity}</div>
                </td>
                <td width='6%'>
                    <div>${line.reconcile_id or '' |entity}</div>
                </td>
            </tr>
            %endfor
            <tr class='celdaTotal'>
                <td colspan="5"></td>
                <td>
                    <div width='6%' >${formatLang(get_total_debit_credit(o.line_id)['sum_tot_debit']) or '0.00' |entity}</div>
                </td>
                <td>
                    <div width='6%'>${formatLang(get_total_debit_credit(o.line_id)['sum_tot_credit']) or '0.00' |entity}</div>
                </td>
                <td colspan="8"></td>
            </tr>
            
        </table>
        %if len(loop._iterable) != 1 and loop.index != len(loop._iterable)-1:
            <p style="page-break-after:always"></p>
        %endif
    %endfor
    </body>
</html>
