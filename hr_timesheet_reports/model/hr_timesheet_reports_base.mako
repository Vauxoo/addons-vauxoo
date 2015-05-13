<!DOCTYPE html SYSTEM
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<html>
<head>
    <style type="text/css">
        ${css}
        body {
            font-size: 9px;
        }
        p {
            font-size: 9px;
            line-height: 11px;
        }
        .red {
            color: red;
        }
        .green {
            color: green;
        }
        .blue {
            color: blue;
        }
        .bold {
            color: grey;
            font-weight: bold;
        }
        table p {
            font-size: 9px;
            line-height: 9px;
            padding: 0px;
            padding-bottom: 1px;
            margin: 0px;
        }
        table, th, td {
            border: 1px solid grey;
            border-collapse: collapse;
            text-align: center;
            font-size: 9px;
            padding: 3px;
            vertical-align: top;
        }
        th {
            border: 1px solid black;
        }
        .resume {
            width: 100%;
            border: none;
        }
        .resume > tbody > tr > td{
            text-align: left;
            border: none;
        }
        .totals > td{
            text-align: right;
            font-weight: bold;
        }
        .resume > tbody > tr > td:first-child{
            width: 40%;
        }
        .description {
            text-align: left;
        }
        .duration {
            font-weight: bold;
        }
        .date {
            font-weight: bold;
            width: 10%;
        }
        .paid {
            color: green;
        }
        .unpaid {
            color: red;
        }
        .invoices_content table,
        .invoices_content th,
        .invoices_content td {
            border: none;
            text-align: center;
            font-size: 9px;
            padding: 3px;
            vertical-align: top;
        }
        .invoices_content td {
            width: 20%;
        }
        .invoices_content td.amount {
            text-align: right;
            width: 40%;
        }
        /**
        Fonts Size
        */
        h1, h2, h3, h4, h5 { line-height: auto; }
        h1 { font-size: 14px; }
        h2 { font-size: 13px; }
        h3 { font-size: 12px; }
        h4, h5 { font-size: 11px; }
        table.endpage
        {
            page-break-after: always;
        }
    </style>
</head>
<body style="border:0;">
    %for obj in objects :
        <h2>Report Name: ${obj.name}</h2>
        <h3>
            Resumed Report.
        </h3>
        <h4>Filter Name: ${obj.filter_id.name}</h4>
        <table class="resume endpage">
            <tbody>
            <tr>
            <td>
                <p>
                ${obj.comment_timesheet}
                </p>
            </td>
            <td>
                <table>
                    <tr class="by_account">
                        <td colspan="3"> By Date </td>
                    </tr>
                    <tr class="title">
                        <td> Month </td>
                        <td> Total Hours</td>
                        <td> Billable Hours</td>
                    </tr>
                    %for resume in obj.records['resume_month'] :
                        <tr class="by_account">
                            <td style="text-align: left;">
                            ${resume.get('date')}
                            </td>
                            <td>
                            ${formatLang(resume.get('unit_amount'))}
                            </td>
                            <td>
                            ${formatLang(resume.get('invoiceables_hours', '0.00'))}
                            </td>
                        </tr>
                    %endfor
                        <tr class="totals">
                            <td>Totals</td>
                            <td>${formatLang(obj.records.get('total_ts_by_month'))}</td>
                            <td>${formatLang(obj.records.get('total_ts_bill_by_month'))}</td>
                        </tr>
                </table>
            </td>
            <td>
                <table>
                    <tr class="by_account">
                        <td colspan="3"> By Analytic </td>
                    </tr>
                    <tr class="title">
                        <td> Account </td>
                        <td> Total Hours</td>
                        <td> Billable Hours</td>
                    </tr>
                    %for resume in obj.records['resume'] :
                    <tr class="by_account">
                        <td style="text-align: left;">
                        ${resume.get('account_id')[1].split('/')[-1]}
                        </td>
                        <td>
                        ${formatLang(resume.get('unit_amount', '0.00'))}
                        </td>
                        <td>
                        ${formatLang(resume.get('invoiceables_hours', '0.00'))}
                        </td>
                    </tr>
                    %endfor
                    <tr class="totals">
                        <td>Totals</td>
                        <td>${formatLang(obj.records.get('total_ts_by_month'))}</td>
                        <td>${formatLang(obj.records.get('total_ts_bill_by_month'))}</td>
                    </tr>
                </table>
            </td>
            </tr>
            <tr>
                <td>
                </td>
                <td>
                </td>
            </tr>
            </tbody>
        </table>
        <table class="endpage">
            <tbody>
            % if obj.records.get('invoices', []):
            <tr>
            <td>
                <p>
                ${obj.comment_invoices}
                </p>
            </td>
            <td colspan="2">
                <table width="100%">
                <tr class="by_account">
                    <td colspan="3">Status of invoices until today in the project.</td>
                </tr>
                <tr class="title">
                    <td width="10%"> Period </td>
                    <td style="padding: 0px;" colspan="2">
                        <table width="100%">
                            <tr>
                            <td width="30%"> Invoice Number </td>
                            <td width="35%"> Total (Currency)</td>
                            <td width="35%"> Pending (Currency)</td>
                            </tr>
                        </table>
                    </td>
                </tr>
                %for period in obj.records['periods'] :
                    <tr>
                        <td width="10%" style="text-align: left;">
                        ${period.get('period_id')[1]}
                        </td>
                        <td colspan="2" width="40%" class="invoices_content">
                            <table width="100%">
                                %for invoice in obj.records['invoices'] :
                                    % if invoice.period_id.id == period.get('period_id')[0]:
                                    % if invoice.residual > 1.00:
                                    <tr class="unpaid">
                                    % endif
                                    % if invoice.residual < 1.00:
                                    <tr class="paid">
                                    % endif
                                        <td> ${invoice.number} </td>
                                        <td class="amount"> ${formatLang(invoice.amount_total)} ( ${invoice.currency_id.name} )</td>
                                        <td class="amount"> ${formatLang(invoice.residual)} ( ${invoice.currency_id.name} )</td>
                                    </tr>
                                    % endif
                                %endfor
                            </table>
                        </td>
                    </tr>
                %endfor
                %for currency in obj.records['total_invoices'] :
                <tr class="totals">
                    <td> Total in ${currency.get('currency_id')[1]} </td>
                    <td>${formatLang(currency.get('amount_total'))} </td>
                    <td>${formatLang(currency.get('residual'))} </td>
                </tr>
                %endfor
                </table>
            </td>
            </tr>
            % endif
            </tbody>
        </table>
        % if obj.records.get('issues', []):
        <h3> Issues. </h3>
        <h4>Filter Name: ${obj.filter_issue_id.name}</h4>
        <table class="resume endpage">
            <tbody>
            <tr>
            <td>
                <p>
                ${obj.comment_issues}
                </p>
            </td>
            <td>
                <table width="100%">
                    <tbody>
                    <tr>
                        <td colspan="3">Status of issues until today in the project.</td>
                    </tr>
                    <tr>
                        <td width="60%"> Analytic Account </td>
                        <td width="10%"> Qty </td>
                        <td width="30%"> Status </td>
                    </tr>
                    %for issue in obj.records['issues'] :
                    <tr>
                        <td width="60%" style="text-align: left;">
                            ${issue.get('analytic_account_id') and issue.get('analytic_account_id')[1] or 'Not analytic Setted.' }
                        </td>
                        <td  width="10%" class="invoices_content">
                            ${issue['analytic_account_id_count']}
                        </td>
                        <td  width="30%" style="text-align: right;" class="invoices_content">
                            %for stage in issue['children_by_stage'] :
                            <p style="padding-top:2px;">${stage['stage_id'][1]} - ${stage['stage_id_count']}</p>
                            %endfor
                        </td>
                    </tr>
                    %endfor
                    </tbody>
                </table>
            </td>
            </tr>
            </tbody>
        </table>
        % endif
        % if obj.records.get('user_stories', []):
        <h3> User Stories. </h3>
        <h4>Filter Name: ${obj.filter_hu_id.name}</h4>
        <table class="resume endpage">
            <tbody>
            <tr>
            <td>
                <p>
                    ${obj.comment_hu}
                </p>
            </td>
            <td>
            <table width="100%">
                <tr class="by_account">
                    <td colspan="7">Status of User Stories until today in the project.</td>
                </tr>
                <tr class="title">
                    <td width="10%"> ID </td>
                    <td width="35%"> Title </td>
                    <td width="15%"> Asked By </td>
                    <td width="10%"> Planned </td>
                    <td width="10%"> Effective </td>
                    <td width="10%"> Invoiceable </td>
                    <td width="10%"> Status </td>
                </tr>
                %for hu in obj.records['user_stories'] :
                <tr>
                    <td width="10%" style="text-align: left;">
                        ${hu.id}
                    </td>
                    <td  width="35%" class="description">
                        ${hu.name}
                    </td>
                    <td  width="15%" class="invoices_content" style="text-align: left;">
                        ${hu.owner_id.name}
                    </td>
                    <td  width="10%" class="invoices_content">
                        ${hu.planned_hours}
                    </td>
                    <td  width="10%" class="invoices_content">
                        ${hu.effective_hours}
                    </td>
                    <td  width="10%" class="invoices_content">
                        ${hu.invoiceable_hours}
                    </td>
                    <td  width="10%" style="text-align: right;" class="invoices_content">
                        ${hu.state}
                    </td>
                </tr>
                %endfor
            </table>
            </td>
            </tr>
            </tbody>
        </table>
        % endif
        <h3> Detailed Report. </h3>
        %for res in obj.records['data'] :
        <table width="100%" style="font-size: 14px;">
            <tr>
                <th colspan="7">
                <h3><b>Analytic Account:</b> ${res}</h3>
                </th>
            </tr>
            <tr>
                <th width="5%"> ID </th>
                <th width="10%"> User </th>
                <th> Description </th>
                <th> Date </th>
                <th> Duration </th>
                <th> Bill </th>
                <th> Invoiceables </th>
            </tr>
            %for rec in obj.records['data'][res] :
                %if not rec['to_invoice'] :
            <tr class="red">
                % elif rec['to_invoice'].id == 1 :
            <tr class="bold">
                % elif rec['to_invoice'].id == 5 :
            <tr class="green">
                % else :
            <tr class="blue">
                % endif
                <td width="5%">
                    ${rec['id']}
                </td>
                <td width="10%">
                    ${rec['author']}
                </td>
                <td class="description">
                    ${rec['description']}
                </td>
                <td class="date">
                    ${rec['date']}
                </td>
                <td class="duration">
                    ${formatLang(rec['duration'], digits=2)}
                </td>
                <td>
                    ${rec['to_invoice'] and rec['to_invoice'].name or 'No Setted'}
                </td>
                <td class="duration">
                    ${formatLang(rec['invoiceables_hours'], digits=2)}
                </td>
            </tr>
            %endfor
        </table>
        %endfor
    <p>
    </p>
%endfor
</body>
</html>
