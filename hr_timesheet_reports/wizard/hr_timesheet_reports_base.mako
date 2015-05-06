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
            text-align: left;
            border: none;
        }
        .description {
            text-align: left;
        }
        .duration {
            font-weight: bold;
        }
        .date {
            font-weight: bold;
        }
        h1, h2, h3, h4, h5 {
            font-size: 10px;
            line-height: auto;
        }
    </style>
</head>
<body style="border:0;">
    %for obj in objects :
        <h2>Report Name: ${obj.filter_id.name}</h2>
        <h3>
            Resumed Report.
        </h3>
        <table class="resume" style="border: none">
            <td style="border: none">
                <table>
                    <tr class="by_account">
                        <td colspan="2">
                        By Date
                        </td>
                    </tr>
                    <tr class="title">
                        <td>
                            Month
                        </td>
                        <td>
                            Hours
                        </td>
                    </tr>
                    %for resume in obj.records['resume_month'] :
                        <tr class="by_account">
                            <td style="text-align: left;">
                            ${resume.get('date')}
                            </td>
                            <td>
                            ${formatLang(resume.get('unit_amount'))}
                            </td>
                        </tr>
                    %endfor
                </table>
            </td>
            <td style="border: none">
                <table>
                    <tr class="by_account">
                        <td colspan="2">
                            By Analytic
                        </td>
                    </tr>
                    <tr class="title">
                        <td>
                            Account
                        </td>
                        <td>
                            Hours
                        </td>
                    </tr>
                    %for resume in obj.records['resume'] :
                    <tr class="by_account">
                        <td style="text-align: left;">
                        ${resume.get('account_id')[1].split('/')[-1]}
                        </td>
                        <td>
                        ${formatLang(resume.get('unit_amount', '0.00'))}
                        </td>
                    </tr>
                    %endfor
                </table>
            </td>
        </table>
        % if obj.records.get('invoices', []):
        <h3>
            Total Invoiced.
        </h3>
        <p>${obj.records['invoices']}</p>
        <table width="100%">
        <tr class="title">
            <td width="10%">
                Period
            </td>
            <td>
                Number
            </td>
        </tr>
        %for period in obj.records['periods'] :
            <tr class="by_account">
                <td width="10%" style="text-align: left;">
                ${period.get('period_id')[1]}
                </td>
                <td>
                ${'( ' + str(period.get('period_id_count', '0')) + ' )'}
                <table width="100%">
                    <tr>
                    <td>
                    Invoice Number
                    </td>
                    <td>
                    Total
                    </td>
                    <td>
                    Currency
                    </td>
                    </tr>
                    %for invoice in period['invoices'] :
                    <tr>
                    </tr>
                    %endfor
                </table>
                </td>
            </tr>
        %endfor
        <tr class="by_account">
            <td colspan="2">
                Total invoiced until today in the project.
            </td>
        </tr>
        </table>
        % endif
        <h3>
            Detailed Report.
        </h3>
        %for res in obj.records['data'] :
        <table width="100%" style="font-size: 14px;">
            <tr>
                <th colspan="5">
                <h3><b>Analytic Account:</b> ${res}</h3>
                </th>
            </tr>
            <tr>
                <th width="5%">
                ID
                </th>
                <th width="10%">
                User
                </th>
                <th>
                Description
                </th>
                <th>
                Date
                </th>
                <th>
                Duration
                </th>
            </tr>
            %for rec in obj.records['data'][res] :
            <tr>
                <td width="5%">
                    ${rec['id']}
                </td>
                <td width="10%">
                    ${rec['author']}
                </td>
                <td class="description">
                    ${rec['description']}
                </td>
                <td class="date" width="10%">
                    ${rec['date']}
                </td>
                <td class="duration">
                    ${formatLang(rec['duration'], digits=2)}
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
