<!DOCTYPE html SYSTEM
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<html>
<head>
    <style type="text/css">
        body {
            font-size: 9px;
        }
        p {
            font-size: 9px;
            line-height: 11px;
        }
        li {
            font-size: 10px;
            line-height: 12px;
        }
        table .title {
            background-color: #A41D35;
            color: white;
            font-weight: bold;
            font-size: 10px;
            line-height: 12px;
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
        .analysis > tbody > tr > td {
            text-align: left;
            border: none;
            width: 50%;
        }
        .analysis p{
            line-height: 12px;
        }
        .analysis h4{
            text-align: center;
        }
        .analysis {
            width: 100%;
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
        h1, h1, h3, h4, h5 { line-height: auto; }
        h1 { font-size: 14px; }
        h1 { font-size: 13px; }
        h3 { font-size: 12px; }
        h4, h5 { font-size: 11px; }
        table.endpage,
        div.endpage
        {
            page-break-after: always;
        }
        section, .raw, div {
            width: 100%;
            border: none;
            overflow: hidden; /* add this to contain floated children */
        }
        div[class^='col-md'] {
             float:left;
        }
        div[class^='col-md'] p,
        .totals p {
            font-size: 11px;
            line-height: 13px;
        }
        .col-md-6 {
            width: 48%;
            padding-right: 4px;
            padding-left: 4px;
        }

    </style>
</head>
<body style="border:0;">
    %for obj in objects :
<div class="endpage">
<div class="col-md-6">
    <h1>Report Name: ${obj.name}</h1>
    <h3>
        Resumed Timesheet Report.
    </h3>
    <h4>Filter Name: ${obj.filter_id.name}</h4>
    <p>
    ${obj.comment_timesheet}
    </p>
</div>
<div class="col-md-6">
    <section>
                <table width="100%">
                    <tr class="title">
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
                            ${resume.get('date')} ( ${resume.get('date_count')} )
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
    </section>
    <section>
                <table width="100%">
                    <tr class="title">
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
                            ${resume.get('account_id')[1].split('/')[-1] } ( ${resume.get('account_id_count')} )
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
    </section>
    <section>
                <table width="100%">
                        <tr class="title">
                            <td colspan="3"> By User </td>
                        </tr>
                        <tr class="title">
                            <td> User </td>
                            <td> Total Hours</td>
                            <td> Billable Hours</td>
                        </tr>
                        %for resume in obj.records['resume_user'] :
                        <tr class="by_account">
                            <td style="text-align: left;">
                            ${resume.get('user_id')[1].split('/')[-1]} ( ${resume.get('user_id_count')} )
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
    </section>
</div>
</div>

% if obj.records.get('invoices', []):
<div class="endpage">
<div class="col-md-6">
    <h2>Economical Status</h2>
    <h3>Filter name: ${obj.filter_invoice_id.name}</h3>
    <p>
    ${obj.comment_invoices}
    </p>
</div>
<div class="col-md-6">
        <table width="100%">
            <tr class="title">
                <td colspan="2">Status of invoices until today in the project.</td>
            </tr>
            <tr class="title">
                <td width="10%"> Period </td>
                <td class="invoices_content" style="padding: 0px;" colspan="2">
                    <table width="100%">
                        <tr>
                            <td width="10%"> Number </td>
                            <td width="20%"> Total </td>
                            <td width="20%"> Tax</td>
                            <td width="20%"> Total</td>
                            <td width="20%"> Pending</td>
                            <td width="10%"> Currency </td>
                        </tr>
                    </table>
                </td>
            </tr>
            %for period in obj.records['periods'] :
            <tr>
                <td width="10%" style="text-align: left;">
                ${period.get('period_id')[1]}
                </td>
                <td colspan="2" class="invoices_content">
                    <table width="100%">
                        %for invoice in obj.records['invoices'] :
                            % if invoice.period_id.id == period.get('period_id')[0]:
                            % if invoice.residual > 1.00:
                            <tr class="unpaid">
                            % endif
                            % if invoice.residual < 1.00:
                            <tr class="paid">
                            % endif
                                <td width="10%"> ${invoice.number} </td>
                                <td width="20%"> ${formatLang(invoice.amount_untaxed)}</td>
                                <td width="20%"> ${formatLang(invoice.amount_tax)}</td>
                                <td width="20%"> ${formatLang(invoice.amount_total)}</td>
                                <td width="20%"> ${formatLang(invoice.residual)}</td>
                                <td width="10%"> ${invoice.currency_id.name} </td>
                            </tr>
                            % endif
                        %endfor
                    </table>
                </td>
            </tr>
            %endfor
            <tr>
                <td class="invoices_content">
                    <table width="100%">
                    %for currency in obj.records['total_invoices'] :
                    <tr>
                        <td> ${currency.get('currency_id')[1]} </td>
                    </tr>
                    %endfor
                    </table>
                </td>
                <td class="invoices_content">
                    <table width="100%">
                    %for currency in obj.records['total_invoices'] :
                    <tr>
                        <td width="10%"> </td>
                        <td width="20%">${formatLang(currency.get('amount_untaxed'))} </td>
                        <td width="20%">${formatLang(currency.get('amount_tax'))} </td>
                        <td width="20%">${formatLang(currency.get('amount_total'))} </td>
                        <td width="20%">${formatLang(currency.get('residual'))} </td>
                        <td width="10%"> </td>
                    </tr>
                    %endfor
                    </table>
                </td>
            </tr>
        </table>
        <section>
            <h2><u>Numbers Explained</u></h2>
            %for il in obj.records.get('resume_product', []):
            <div class="col-md-6">
                <h3><u>Amounts in Currency ${il}: </u></h3>
                <p><b>Training: </b>${formatLang(obj.records.get('resume_product')[il]['training'])}</p>
                <p><b>Consultancy: </b>${formatLang(obj.records.get('resume_product')[il]['consultancy'])}</p>
                <p><b>Enterprises: </b>${formatLang(obj.records.get('resume_product')[il]['enterprises'])}</p>
                <p><b>Others: </b>${formatLang(obj.records.get('resume_product')[il]['others'])}</p>
                <hr/>
                <p><b>Total: </b>${formatLang(obj.records.get('resume_product')[il]['total'])}</p>
                <hr/>
                <p><b>Total in <u>${obj.currency_id.name}</u>: </b>${formatLang(obj.records.get('resume_product')[il]['total_in_control'])}</p>
                <hr/>
                <p><b>Conversion Rate: </b>${formatLang(obj.records.get('resume_product')[il]['conversion_rate'])}</p>
            </div>
            %endfor
        </section>
        <hr/>
        <section>
            <h2><u>Resumed amounts in ${obj.currency_id.name}</u></h2>
            <div class="col-md-6">
            <p><b>Total Invoiced</b>
            <ul>
                <li><b>Training: </b>${sum([obj.records.get('resume_product')[o]['total_train'] for o in obj.records.get('resume_product')])}</li>
                <li><b>Consultancy: </b>${sum([obj.records.get('resume_product')[o]['total_cons'] for o in obj.records.get('resume_product')])}</li>
                <li><b>Enterprises: </b>${sum([obj.records.get('resume_product')[o]['total_lic'] for o in obj.records.get('resume_product')])}</li>
                <li><b>Others: </b>${sum([obj.records.get('resume_product')[o]['total_others'] for o in obj.records.get('resume_product')])}</li>
            </ul>
            </p>
            </div>
            <div class="col-md-6">
            <p><b>Totals Timesheet</b>
            <ul>
                <li><b>Billable: </b>${formatLang(obj.records.get('resumed_numbers')['pending'])}</li>
                <li><b>Pending <br/><sub>Billables - Billed</sub>: </b><br/>${formatLang(obj.records.get('resumed_numbers')['pending'] -sum([obj.records.get('resume_product')[o]['total_cons'] for o in obj.records.get('resume_product')]))}</li>
            </ul>
            </p>
            </div>
        </section>
</div>
</div>
% endif
% if obj.records.get('issues', []):
<div class="endpage">
<div class="col-md-6">
    <h3> Issues. </h3>
    <h4>Filter Name: ${obj.filter_issue_id.name}</h4>
    <p>
        ${obj.comment_issues}
    </p>
</div>
<div class="col-md-6">
    <table width="100%">
        <tbody>
        <tr class="title">
            <td colspan="3">Status of issues until today in the project.</td>
        </tr>
        <tr class="title">
            <td width="50%"> Analytic Account </td>
            <td width="10%"> Qty </td>
            <td width="40%"> Status </td>
        </tr>
        %for issue in obj.records['issues'] :
        <tr>
            <td width="50%" style="text-align: left;">
                ${issue.get('analytic_account_id') and issue.get('analytic_account_id')[1] or 'Not analytic Setted.' }
            </td>
            <td  width="10%" class="invoices_content">
                ${issue['analytic_account_id_count']}
            </td>
            <td  width="40%" style="text-align: right;" class="invoices_content">
                %for stage in issue['children_by_stage'] :
                <p style="padding-top:2px;">${stage['stage_id'][1]} - ${stage['stage_id_count']}</p>
                %endfor
            </td>
        </tr>
        %endfor
        </tbody>
    </table>
</div>
</div>
        % endif
        % if obj.records.get('user_stories', []):
<div class="endpage">
<div class="col-md-6">
    <h3> User Stories. </h3>
    <h4>Filter Name: ${obj.filter_hu_id.name}</h4>
    <p>
        ${obj.comment_hu}
    </p>
</div>
<div class="col-md-6">
    <table width="100%">
        <tr class="title">
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
</div>
</div>
        % endif
        % if obj.show_details:
        <h3> Detailed Report. </h3>
        %for res in obj.records['data'] :
        <table width="100%" style="font-size: 12px;">
            <tr>
                <th colspan="10">
                <h3><b>Analytic Account:</b> ${res}</h3>
                </th>
            </tr>
            <tr>
                <th width="5%"> ID </th>
                <th> Issue </th>
                <th> User Story </th>
                <th> Invoice </th>
                <th width="10%"> User </th>
                <th> Task </th>
                <th> Description </th>
                <th> Date </th>
                <th> Duration </th>
                <th> Bill </th>
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
                <td>
                    ${rec['issue']}
                </td>
                <td>
                    ${rec['task_id'].userstory_id and rec['task_id'].userstory_id.id  or 'Na'}
                </td>
                <td>
                    ${rec['invoice_id'] and rec['invoice_id'] or 'N-I'}
                </td>
                <td width="10%">
                    ${rec['author']}
                </td>
                <td class="description">
                    ${rec['task_id'] and rec['task_id'].id }: ${rec['description']}
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
        %endif
%endfor
</body>
</html>
