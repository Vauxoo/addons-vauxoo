<!DOCTYPE html SYSTEM
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<html>
<head>
    <style type="text/css">
        ${css}
        table, th, td {
            border: 1px solid grey;
            border-collapse: collapse;
            font-size: 12px;
            text-align: center;
        }
        .duration {
            font-size: 9px;
            font-weight: bold;
        }
        .date {
            font-size: 9px;
            font-weight: bold;
        }
    </style>
</head>
<body style="border:0;"> 
    %for obj in objects :
     <table width="100%" style="font-size: 14px;">
        <tr>
            <th width="10%">
               <p>User</p>
            </th>
            <th>
               <p>Description</p>
            </th>
            <th>
               <p>Date</p>
            </th>
            <th>
               <p>Duration</p>
            </th>
        </tr>
        %for rec in obj.records :
        <tr>
            <td width="10%">
                <p>${rec['author']}</p>
            </td>
            <td>
                <p>${rec['description']}</p>
            </td>
            <td class="date" width="10%">
                <p>${rec['date']}</p>
            </td>
            <td class="duration">
                <p>${formatLang(rec['duration'], digits=2)}</p>
            </td>
        </tr>
        %endfor
     </table>
    <p>
    </p>
%endfor
</body>
</html>
